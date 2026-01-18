# Maptoposter Web

Generate beautiful, minimalist map posters for any city with a web-first workflow and advanced controls.

<img src="posters/singapore_neon_cyberpunk_20260108_184503.png" width="250">
<img src="posters/dubai_midnight_blue_20260108_174920.png" width="250">

## Examples


| Country      | City           | Theme           | Poster |
|:------------:|:--------------:|:---------------:|:------:|
| USA          | San Francisco  | sunset          | <img src="posters/san_francisco_sunset_20260108_184122.png" width="250"> |
| Spain        | Barcelona      | warm_beige      | <img src="posters/barcelona_warm_beige_20260108_172924.png" width="250"> |
| Italy        | Venice         | blueprint       | <img src="posters/venice_blueprint_20260108_165527.png" width="250"> |
| Japan        | Tokyo          | japanese_ink    | <img src="posters/tokyo_japanese_ink_20260108_165830.png" width="250"> |
| India        | Mumbai         | contrast_zones  | <img src="posters/mumbai_contrast_zones_20260108_170325.png" width="250"> |
| Morocco      | Marrakech      | terracotta      | <img src="posters/marrakech_terracotta_20260108_180821.png" width="250"> |
| Singapore    | Singapore      | neon_cyberpunk  | <img src="posters/singapore_neon_cyberpunk_20260108_184503.png" width="250"> |
| Australia    | Melbourne      | forest          | <img src="posters/melbourne_forest_20260108_181459.png" width="250"> |
| UAE          | Dubai          | midnight_blue   | <img src="posters/dubai_midnight_blue_20260108_174920.png" width="250"> |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web App

```bash
python app.py
```

Then open `http://localhost:5001`.

### Distance Guide

| Distance | Best for |
|----------|----------|
| 1000-3000m | Very small areas, neighborhoods |
| 4000-6000m | Small/dense cities (Venice, Amsterdam center) |
| 8000-12000m | Medium cities, focused downtown (Paris, Barcelona) |
| 15000-20000m | Large metros, full city view (Tokyo, Mumbai) |

## Themes

Themes are stored in the `themes/` directory (30 total in this repo). Examples:

| Theme | Style |
|-------|-------|
| `autumn` | Burnt oranges, deep reds, golden yellows - seasonal warmth |
| `blueprint` | Classic architectural blueprint - technical drawing aesthetic |
| `chicago_bears` | Navy and orange - classic NFL bold contrast |
| `chicago_bulls` | Red, black, and white - bold, high-contrast palette |
| `chicago_cubs` | Cubs blue with red accents - crisp and classic |
| `contrast_zones` | Strong contrast showing urban density - darker in center, lighter at edges |
| `copper_patina` | Oxidized copper aesthetic - teal-green patina with copper accents |
| `cyberpunk` | Magenta, cyan, and purple neon on a deep midnight base |
| `detroit_lions` | Honolulu blue and silver - clean NFL-inspired palette |
| `detroit_tigers` | Navy and orange - classic baseball palette |
| `feature_based` | Different shades for different road types and features with clear hierarchy |
| `forest` | Deep greens and sage tones - organic botanical aesthetic |
| `gradient_roads` | Smooth gradient from dark center to light edges with subtle features |
| `japanese_ink` | Traditional ink wash inspired - minimalist with subtle red accent |
| `michigan_state` | Green and white - Spartan palette with muted grays |
| `michigan_wolverines` | Maize and blue - iconic U of M colors |
| `midnight_blue` | Deep navy background with gold/copper roads - luxury atlas aesthetic |
| `monochrome_blue` | Single blue color family with varying saturation - clean and cohesive |
| `neon_cyberpunk` | Dark background with electric pink/cyan - bold night city vibes |
| `noir` | Pure black background with white/gray roads - modern gallery aesthetic |
| `ocean` | Various blues and teals - perfect for coastal cities |
| `pastel_dream` | Soft muted pastels with dusty blues and mauves - dreamy artistic aesthetic |
| `pride_lesbian` | Warm oranges, pinks, and plum - vibrant and layered |
| `pride_progress` | Progress Pride colors with strong contrast and warm neutrals |
| `pride_rainbow` | Bold, saturated rainbow accents on a clean light base |
| `pride_rainbow_dark` | Rainbow accents on a deep charcoal base |
| `pride_trans` | Light blues, pinks, and white - soft and clean |
| `sunset` | Warm oranges and pinks on soft peach - dreamy golden hour aesthetic |
| `terracotta` | Mediterranean warmth - burnt orange and clay tones on cream |
| `warm_beige` | Earthy warm neutrals with sepia tones - vintage map aesthetic |

## Output

Posters are saved to `posters/` directory with format:
```
{city}_{theme}_{YYYYMMDD_HHMMSS}.png
```

## Adding Custom Themes

Create a JSON file in `themes/` directory:

```json
{
  "name": "My Theme",
  "description": "Description of the theme",
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
```

## Project Structure

```
maptoposter-web/
├── app.py                        # Flask web app
├── create_map_poster.py          # Main script
├── templates/                    # Web app templates
├── static/                       # Web app assets
├── themes/                       # Theme JSON files
├── fonts/                        # Roboto font files
├── posters/                      # Generated posters
└── README.md
```

## Hacker's Guide

Quick reference for contributors who want to extend or modify the script.

### Architecture Overview

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   CLI Parser    │────▶│  Geocoding   │────▶│  Data Fetching  │
│   (argparse)    │     │  (Nominatim) │     │    (OSMnx)      │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                     │
                        ┌──────────────┐             ▼
                        │    Output    │◀────┌─────────────────┐
                        │  (matplotlib)│     │   Rendering     │
                        └──────────────┘     │  (matplotlib)   │
                                             └─────────────────┘
```

### Key Functions

| Function | Purpose | Modify when... |
|----------|---------|----------------|
| `get_coordinates()` | City → lat/lon via Nominatim | Switching geocoding provider |
| `create_poster()` | Main rendering pipeline | Adding new map layers or visual controls |
| `get_edge_colors_by_type()` | Road color by OSM highway tag | Changing road styling |
| `get_edge_widths_by_type()` | Road width by importance | Adjusting line weights |
| `create_gradient_fade()` | Top/bottom fade effect | Modifying gradient overlay |
| `load_theme()` | JSON theme → dict | Adding new theme properties |

### Rendering Layers (z-order)

```
z=11  Text labels (city, country, coords)
z=10  Gradient fades (top & bottom)
z=3   Roads (via ox.plot_graph)
z=2   Parks (green polygons)
z=1   Water (blue polygons)
z=0   Background color
```

### Web App Advanced Controls

The web UI exposes the core pipeline knobs via an `options` payload:
- Road hierarchy toggles (colors + widths)
- Network type toggles (drive/bike/walk, or none)
- Extra layers (parks, water, buildings, railways)
- Custom layer builder (tag key/value + style)
- Custom layer presets (saved per browser, export/import/delete)
- Typography positions (normalized axes Y values)
- Gradient fade toggle

### OSM Highway Types → Road Hierarchy

```python
# In get_edge_colors_by_type() and get_edge_widths_by_type()
motorway, motorway_link     → Thickest (1.2), darkest
trunk, primary              → Thick (1.0)
secondary                   → Medium (0.8)
tertiary                    → Thin (0.6)
residential, living_street  → Thinnest (0.4), lightest
```

### Adding New Features

**New map layer (e.g., railways):**
```python
# In create_poster(), after parks fetch:
try:
    railways = ox.features_from_point(point, tags={'railway': 'rail'}, dist=dist)
except:
    railways = None

# Then plot before roads:
if railways is not None and not railways.empty:
    railways.plot(ax=ax, color=THEME['railway'], linewidth=0.5, zorder=2.5)
```

**New theme property:**
1. Add to theme JSON: `"railway": "#FF0000"`
2. Use in code: `THEME['railway']`
3. Add fallback in `load_theme()` default dict

### Typography Positioning

All text uses `transform=ax.transAxes` (0-1 normalized coordinates):
```
y=0.14  City name (spaced letters)
y=0.125 Decorative line
y=0.10  Country name
y=0.07  Coordinates
y=0.02  Attribution (bottom-right)
```

### Useful OSMnx Patterns

```python
# Get all buildings
buildings = ox.features_from_point(point, tags={'building': True}, dist=dist)

# Get specific amenities
cafes = ox.features_from_point(point, tags={'amenity': 'cafe'}, dist=dist)

# Different network types
G = ox.graph_from_point(point, dist=dist, network_type='drive')  # roads only
G = ox.graph_from_point(point, dist=dist, network_type='bike')   # bike paths
G = ox.graph_from_point(point, dist=dist, network_type='walk')   # pedestrian
```

### Performance Tips

- Large `dist` values (>20km) = slow downloads + memory heavy
- Cache coordinates locally to avoid Nominatim rate limits
- Use `network_type='drive'` instead of `'all'` for faster renders
- Reduce `dpi` from 300 to 150 for quick previews
