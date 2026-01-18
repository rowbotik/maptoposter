import osmnx as ox
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors
import numpy as np
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time
import json
import os
from datetime import datetime
import argparse

THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"

def load_fonts():
    """
    Load Roboto fonts from the fonts directory.
    Returns dict with font paths for different weights.
    """
    fonts = {
        'bold': os.path.join(FONTS_DIR, 'Roboto-Bold.ttf'),
        'regular': os.path.join(FONTS_DIR, 'Roboto-Regular.ttf'),
        'light': os.path.join(FONTS_DIR, 'Roboto-Light.ttf')
    }
    
    # Verify fonts exist
    for weight, path in fonts.items():
        if not os.path.exists(path):
            print(f"⚠ Font not found: {path}")
            return None
    
    return fonts

FONTS = load_fonts()

def generate_output_filename(city, theme_name):
    """
    Generate unique output filename with city, theme, and datetime.
    """
    if not os.path.exists(POSTERS_DIR):
        os.makedirs(POSTERS_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(' ', '_')
    filename = f"{city_slug}_{theme_name}_{timestamp}.png"
    return os.path.join(POSTERS_DIR, filename)

def get_available_themes():
    """
    Scans the themes directory and returns a list of available theme names.
    """
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        return []
    
    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith('.json'):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes

def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    """
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    
    if not os.path.exists(theme_file):
        print(f"⚠ Theme file '{theme_file}' not found. Using default feature_based theme.")
        # Fallback to embedded default theme
        return {
            "name": "Feature-Based Shading",
            "bg": "#FFFFFF",
            "text": "#000000",
            "gradient_color": "#FFFFFF",
            "water": "#C0C0C0",
            "parks": "#F0F0F0",
            "road_motorway": "#0A0A0A",
            "road_primary": "#1A1A1A",
            "road_secondary": "#2A2A2A",
            "road_tertiary": "#3A3A3A",
            "road_residential": "#4A4A4A",
            "road_default": "#3A3A3A"
        }
    
    with open(theme_file, 'r') as f:
        theme = json.load(f)
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if 'description' in theme:
            print(f"  {theme['description']}")
        return theme

# Load theme (can be changed via command line or input)
THEME = None  # Will be loaded later

def create_gradient_fade(ax, color, location='bottom', zorder=10):
    """
    Creates a fade effect at the top or bottom of the map.
    """
    vals = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.hstack((vals, vals))
    
    rgb = mcolors.to_rgb(color)
    my_colors = np.zeros((256, 4))
    my_colors[:, 0] = rgb[0]
    my_colors[:, 1] = rgb[1]
    my_colors[:, 2] = rgb[2]
    
    if location == 'bottom':
        my_colors[:, 3] = np.linspace(1, 0, 256)
        extent_y_start = 0
        extent_y_end = 0.25
    else:
        my_colors[:, 3] = np.linspace(0, 1, 256)
        extent_y_start = 0.75
        extent_y_end = 1.0

    custom_cmap = mcolors.ListedColormap(my_colors)
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]
    
    y_bottom = ylim[0] + y_range * extent_y_start
    y_top = ylim[0] + y_range * extent_y_end
    
    ax.imshow(gradient, extent=[xlim[0], xlim[1], y_bottom, y_top], 
              aspect='auto', cmap=custom_cmap, zorder=zorder, origin='lower')

def get_edge_colors_by_type(G):
    """
    Assigns colors to edges based on road type hierarchy.
    Returns a list of colors corresponding to each edge in the graph.
    """
    edge_colors = []
    
    for u, v, data in G.edges(data=True):
        # Get the highway type (can be a list or string)
        highway = data.get('highway', 'unclassified')
        
        # Handle list of highway types (take the first one)
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign color based on road type
        if highway in ['motorway', 'motorway_link']:
            color = THEME['road_motorway']
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            color = THEME['road_primary']
        elif highway in ['secondary', 'secondary_link']:
            color = THEME['road_secondary']
        elif highway in ['tertiary', 'tertiary_link']:
            color = THEME['road_tertiary']
        elif highway in ['residential', 'living_street', 'unclassified']:
            color = THEME['road_residential']
        else:
            color = THEME['road_default']
        
        edge_colors.append(color)
    
    return edge_colors

def get_edge_widths_by_type(G):
    """
    Assigns line widths to edges based on road type.
    Major roads get thicker lines.
    """
    edge_widths = []
    
    for u, v, data in G.edges(data=True):
        highway = data.get('highway', 'unclassified')
        
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign width based on road importance
        if highway in ['motorway', 'motorway_link']:
            width = 1.2
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            width = 1.0
        elif highway in ['secondary', 'secondary_link']:
            width = 0.8
        elif highway in ['tertiary', 'tertiary_link']:
            width = 0.6
        else:
            width = 0.4
        
        edge_widths.append(width)
    
    return edge_widths

def get_coordinates(city, country):
    """
    Fetches coordinates for a given city and country using geopy.
    Includes rate limiting to be respectful to the geocoding service.
    """
    print("Looking up coordinates...")
    geolocator = Nominatim(user_agent="city_map_poster")
    
    # Add a small delay to respect Nominatim's usage policy
    time.sleep(1)
    
    location = geolocator.geocode(f"{city}, {country}")
    
    if location:
        print(f"✓ Found: {location.address}")
        print(f"✓ Coordinates: {location.latitude}, {location.longitude}")
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Could not find coordinates for {city}, {country}")

def _format_coordinates(lat, lon):
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}° {lat_dir} / {abs(lon):.4f}° {lon_dir}"


def _merge_options(options):
    defaults = {
        "network_types": ["all"],
        "use_cache": True,
        "show_water": True,
        "show_parks": True,
        "show_buildings": False,
        "show_railways": False,
        "show_gradients": True,
        "use_road_hierarchy_colors": True,
        "use_road_hierarchy_widths": True,
        "road_color": None,
        "road_width": 0.6,
        "building_color": None,
        "building_alpha": 0.4,
        "railway_color": None,
        "railway_width": 0.6,
        "custom_layers": [],
        "typography_positions": {
            "city_y": 0.14,
            "line_y": 0.125,
            "country_y": 0.10,
            "coords_y": 0.07,
            "attribution_y": 0.02
        }
    }

    if not options:
        return defaults

    merged = defaults.copy()
    merged.update(options)
    merged["typography_positions"] = {
        **defaults["typography_positions"],
        **options.get("typography_positions", {})
    }
    return merged


def _plot_custom_layer(ax, layer_data, style):
    if layer_data is None or layer_data.empty:
        return

    color = style.get("color", "#333333")
    alpha = style.get("alpha", 1.0)
    zorder = style.get("zorder", 2.5)
    line_width = style.get("line_width", 0.5)
    mode = style.get("mode", "line")

    if mode == "fill":
        layer_data.plot(
            ax=ax,
            facecolor=color,
            edgecolor="none",
            alpha=alpha,
            zorder=zorder
        )
    else:
        layer_data.plot(
            ax=ax,
            color=color,
            linewidth=line_width,
            alpha=alpha,
            zorder=zorder
        )


def create_poster(city, country, point, dist, output_file, options=None):
    print(f"\nGenerating map for {city}, {country}...")

    options = _merge_options(options)
    network_types = options.get("network_types", ["all"])
    if isinstance(network_types, str):
        network_types = [network_types]

    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    ox.settings.use_cache = bool(options.get("use_cache", True))
    ox.settings.cache_folder = cache_dir

    custom_layers = [
        layer for layer in (options.get("custom_layers") or [])
        if isinstance(layer, dict) and layer.get("tag_key")
    ]

    fetch_steps = 0 if not network_types else 1
    if options["show_water"]:
        fetch_steps += 1
    if options["show_parks"]:
        fetch_steps += 1
    if options["show_buildings"]:
        fetch_steps += 1
    if options["show_railways"]:
        fetch_steps += 1
    fetch_steps += len(custom_layers)

    # Progress bar for data fetching
    with tqdm(total=fetch_steps, desc="Fetching map data", unit="step", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        # 1. Fetch Street Network
        G = None
        if network_types:
            if "all" in network_types:
                pbar.set_description("Downloading street network")
                G = ox.graph_from_point(point, dist=dist, dist_type='bbox', network_type='all')
                pbar.update(1)
                time.sleep(0.5)  # Rate limit between requests
            else:
                graphs = []
                for net_type in network_types:
                    pbar.set_description(f"Downloading {net_type} network")
                    graphs.append(
                        ox.graph_from_point(point, dist=dist, dist_type='bbox', network_type=net_type)
                    )
                    pbar.update(1)
                    time.sleep(0.3)
                if graphs:
                    G = nx.compose_all(graphs)

        water = None
        if options["show_water"]:
            pbar.set_description("Downloading water features")
            try:
                water = ox.features_from_point(point, tags={'natural': 'water', 'waterway': 'riverbank'}, dist=dist)
            except:
                water = None
            pbar.update(1)
            time.sleep(0.3)

        parks = None
        if options["show_parks"]:
            pbar.set_description("Downloading parks/green spaces")
            try:
                parks = ox.features_from_point(point, tags={'leisure': 'park', 'landuse': 'grass'}, dist=dist)
            except:
                parks = None
            pbar.update(1)

        buildings = None
        if options["show_buildings"]:
            pbar.set_description("Downloading buildings")
            try:
                buildings = ox.features_from_point(point, tags={'building': True}, dist=dist)
            except:
                buildings = None
            pbar.update(1)

        railways = None
        if options["show_railways"]:
            pbar.set_description("Downloading railways")
            try:
                railways = ox.features_from_point(point, tags={'railway': 'rail'}, dist=dist)
            except:
                railways = None
            pbar.update(1)

        custom_layer_data = []
        for layer in custom_layers:
            key = layer.get("tag_key")
            if not key:
                continue
            tag_value = layer.get("tag_value")
            tags = {key: True if tag_value in (None, "", "true", "True") else tag_value}
            pbar.set_description(f"Downloading {key} layer")
            try:
                layer_data = ox.features_from_point(point, tags=tags, dist=dist)
            except:
                layer_data = None
            custom_layer_data.append((layer_data, layer))
            pbar.update(1)
    
    print("✓ All data downloaded successfully!")
    
    # 2. Setup Plot
    print("Rendering map...")
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    ax.set_position([0, 0, 1, 1])
    
    # 3. Plot Layers
    # Layer 1: Polygons
    if water is not None and not water.empty:
        water.plot(ax=ax, facecolor=THEME['water'], edgecolor='none', zorder=1)
    if parks is not None and not parks.empty:
        parks.plot(ax=ax, facecolor=THEME['parks'], edgecolor='none', zorder=2)

    if buildings is not None and not buildings.empty:
        building_color = options["building_color"] or THEME.get("road_residential", "#999999")
        buildings.plot(
            ax=ax,
            facecolor=building_color,
            edgecolor="none",
            alpha=options["building_alpha"],
            zorder=2.2
        )

    if railways is not None and not railways.empty:
        railway_color = options["railway_color"] or THEME.get("road_primary", "#666666")
        railways.plot(
            ax=ax,
            color=railway_color,
            linewidth=options["railway_width"],
            alpha=0.9,
            zorder=2.6
        )

    for layer_data, layer_style in custom_layer_data:
        _plot_custom_layer(ax, layer_data, {
            "color": layer_style.get("color", "#333333"),
            "alpha": layer_style.get("alpha", 1.0),
            "zorder": layer_style.get("zorder", 2.5),
            "line_width": layer_style.get("line_width", 0.5),
            "mode": layer_style.get("mode", "line")
        })
    
    # Layer 2: Roads with hierarchy coloring
    if G is not None and len(G.edges) > 0:
        print("Applying road hierarchy colors...")
        if options["use_road_hierarchy_colors"]:
            edge_colors = get_edge_colors_by_type(G)
        else:
            road_color = options["road_color"] or THEME.get("road_default", "#333333")
            edge_colors = [road_color] * len(G.edges)

        if options["use_road_hierarchy_widths"]:
            edge_widths = get_edge_widths_by_type(G)
        else:
            edge_widths = [options["road_width"]] * len(G.edges)
        
        ox.plot_graph(
            G, ax=ax, bgcolor=THEME['bg'],
            node_size=0,
            edge_color=edge_colors,
            edge_linewidth=edge_widths,
            show=False, close=False
        )
    
    # Layer 3: Gradients (Top and Bottom)
    if options["show_gradients"]:
        create_gradient_fade(ax, THEME['gradient_color'], location='bottom', zorder=10)
        create_gradient_fade(ax, THEME['gradient_color'], location='top', zorder=10)
    
    # 4. Typography using Roboto font
    if FONTS:
        font_main = FontProperties(fname=FONTS['bold'], size=60)
        font_top = FontProperties(fname=FONTS['bold'], size=40)
        font_sub = FontProperties(fname=FONTS['light'], size=22)
        font_coords = FontProperties(fname=FONTS['regular'], size=14)
    else:
        # Fallback to system fonts
        font_main = FontProperties(family='monospace', weight='bold', size=60)
        font_top = FontProperties(family='monospace', weight='bold', size=40)
        font_sub = FontProperties(family='monospace', weight='normal', size=22)
        font_coords = FontProperties(family='monospace', size=14)
    
    spaced_city = "  ".join(list(city.upper()))

    # --- BOTTOM TEXT ---
    text_positions = options["typography_positions"]

    ax.text(0.5, text_positions["city_y"], spaced_city, transform=ax.transAxes,
            color=THEME['text'], ha='center', fontproperties=font_main, zorder=11)
    
    ax.text(0.5, text_positions["country_y"], country.upper(), transform=ax.transAxes,
            color=THEME['text'], ha='center', fontproperties=font_sub, zorder=11)
    
    lat, lon = point
    coords = _format_coordinates(lat, lon)
    
    ax.text(0.5, text_positions["coords_y"], coords, transform=ax.transAxes,
            color=THEME['text'], alpha=0.7, ha='center', fontproperties=font_coords, zorder=11)
    
    ax.plot([0.4, 0.6], [text_positions["line_y"], text_positions["line_y"]], transform=ax.transAxes, 
            color=THEME['text'], linewidth=1, zorder=11)

    # --- ATTRIBUTION (bottom right) ---
    if FONTS:
        font_attr = FontProperties(fname=FONTS['light'], size=8)
    else:
        font_attr = FontProperties(family='monospace', size=8)
    
    ax.text(0.98, text_positions["attribution_y"], "© OpenStreetMap contributors", transform=ax.transAxes,
            color=THEME['text'], alpha=0.5, ha='right', va='bottom', 
            fontproperties=font_attr, zorder=11)

    # 5. Save
    print(f"Saving to {output_file}...")
    plt.savefig(output_file, dpi=300, facecolor=THEME['bg'])
    plt.close()
    print(f"✓ Done! Poster saved as {output_file}")

def print_examples():
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python create_map_poster.py --city <city> --country <country> [options]

Examples:
  # Iconic grid patterns
  python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000           # Manhattan grid
  python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000   # Eixample district grid
  
  # Waterfront & canals
  python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000       # Canal network
  python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000  # Concentric canals
  python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000     # Palm & coastline
  
  # Radial patterns
  python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000   # Haussmann boulevards
  python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000          # Ring roads
  
  # Organic old cities
  python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000    # Dense organic streets
  python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000 # Medina maze
  python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000        # Ancient street layout
  
  # Coastal cities
  python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000    # Peninsula grid
  python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000      # Harbor city
  python create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000 # Coastal peninsula
  
  # River cities
  python create_map_poster.py -c "London" -C "UK" -t noir -d 15000              # Thames curves
  python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000  # Danube split
  
  # List themes
  python create_map_poster.py --list-themes

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --theme, -t       Theme name (default: feature_based)
  --distance, -d    Map radius in meters (default: 29000)
  --list-themes     List all available themes

Distance guide:
  4000-6000m   Small/dense cities (Venice, Amsterdam old center)
  8000-12000m  Medium cities, focused downtown (Paris, Barcelona)
  15000-20000m Large metros, full city view (Tokyo, Mumbai)

Available themes can be found in the 'themes/' directory.
Generated posters are saved to 'posters/' directory.
""")

def list_themes():
    """List all available themes with descriptions."""
    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        return
    
    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in available_themes:
        theme_path = os.path.join(THEMES_DIR, f"{theme_name}.json")
        try:
            with open(theme_path, 'r') as f:
                theme_data = json.load(f)
                display_name = theme_data.get('name', theme_name)
                description = theme_data.get('description', '')
        except:
            display_name = theme_name
            description = ''
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate beautiful map posters for any city",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_map_poster.py --city "New York" --country "USA"
  python create_map_poster.py --city Tokyo --country Japan --theme midnight_blue
  python create_map_poster.py --city Paris --country France --theme noir --distance 15000
  python create_map_poster.py --list-themes
        """
    )
    
    parser.add_argument('--city', '-c', type=str, help='City name')
    parser.add_argument('--country', '-C', type=str, help='Country name')
    parser.add_argument('--theme', '-t', type=str, default='feature_based', help='Theme name (default: feature_based)')
    parser.add_argument('--distance', '-d', type=int, default=29000, help='Map radius in meters (default: 29000)')
    parser.add_argument('--list-themes', action='store_true', help='List all available themes')
    
    args = parser.parse_args()
    
    # If no arguments provided, show examples
    if len(os.sys.argv) == 1:
        print_examples()
        os.sys.exit(0)
    
    # List themes if requested
    if args.list_themes:
        list_themes()
        os.sys.exit(0)
    
    # Validate required arguments
    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        os.sys.exit(1)
    
    # Validate theme exists
    available_themes = get_available_themes()
    if args.theme not in available_themes:
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available themes: {', '.join(available_themes)}")
        os.sys.exit(1)
    
    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)
    
    # Load theme
    THEME = load_theme(args.theme)
    
    # Get coordinates and generate poster
    try:
        coords = get_coordinates(args.city, args.country)
        output_file = generate_output_filename(args.city, args.theme)
        create_poster(args.city, args.country, coords, args.distance, output_file)
        
        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        os.sys.exit(1)
