#!/usr/bin/env python3
"""
Map Poster Generator - Flask Web Application
Beautiful web interface for generating minimalist city map posters
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import json
import os
import uuid
from pathlib import Path
import threading
import time

from create_map_poster import (
    get_coordinates, create_poster, load_theme,
    get_available_themes, THEMES_DIR, POSTERS_DIR
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store generation status
generation_status = {}

def _safe_resolve(base_dir, filename):
    base_path = Path(base_dir).resolve()
    target_path = (base_path / filename).resolve()
    if base_path != target_path and base_path not in target_path.parents:
        raise ValueError("Invalid path")
    return target_path


def _coerce_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_options(options):
    if not isinstance(options, dict):
        return {}

    network_types = options.get("network_types")
    if network_types is None and "network_type" in options:
        network_types = [options.get("network_type")]
    if not isinstance(network_types, list):
        network_types = ["all"]

    valid_types = {"all", "drive", "bike", "walk"}
    network_types = [nt for nt in network_types if nt in valid_types]

    typography = options.get("typography_positions", {})
    normalized_typography = {
        "city_y": _coerce_float(typography.get("city_y"), 0.14),
        "line_y": _coerce_float(typography.get("line_y"), 0.125),
        "country_y": _coerce_float(typography.get("country_y"), 0.10),
        "coords_y": _coerce_float(typography.get("coords_y"), 0.07),
        "attribution_y": _coerce_float(typography.get("attribution_y"), 0.02)
    }

    custom_layers = options.get("custom_layers") or []
    normalized_layers = []
    for layer in custom_layers:
        if not isinstance(layer, dict):
            continue
        tag_key = layer.get("tag_key")
        tag_key = str(tag_key).strip() if tag_key is not None else ""
        normalized_layers.append({
            "tag_key": tag_key,
            "tag_value": layer.get("tag_value"),
            "mode": layer.get("mode", "line"),
            "color": layer.get("color", "#333333"),
            "line_width": _coerce_float(layer.get("line_width"), 0.5),
            "alpha": _coerce_float(layer.get("alpha"), 1.0),
            "zorder": _coerce_float(layer.get("zorder"), 2.5)
        })

    return {
        "network_types": network_types,
        "use_cache": bool(options.get("use_cache", True)),
        "show_water": bool(options.get("show_water", True)),
        "show_parks": bool(options.get("show_parks", True)),
        "show_buildings": bool(options.get("show_buildings", False)),
        "show_railways": bool(options.get("show_railways", False)),
        "show_gradients": bool(options.get("show_gradients", True)),
        "use_road_hierarchy_colors": bool(options.get("use_road_hierarchy_colors", True)),
        "use_road_hierarchy_widths": bool(options.get("use_road_hierarchy_widths", True)),
        "road_color": options.get("road_color"),
        "road_width": _coerce_float(options.get("road_width"), 0.6),
        "building_color": options.get("building_color"),
        "building_alpha": _coerce_float(options.get("building_alpha"), 0.4),
        "railway_color": options.get("railway_color"),
        "railway_width": _coerce_float(options.get("railway_width"), 0.6),
        "custom_layers": normalized_layers,
        "typography_positions": normalized_typography
    }

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')


@app.route('/theme-creator')
def theme_creator():
    """Theme creator page"""
    return render_template('theme_creator.html')


@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get list of available themes with their data"""
    themes = get_available_themes()
    theme_data = []

    for theme_name in themes:
        try:
            theme = load_theme(theme_name)
            theme_data.append({
                'id': theme_name,
                'name': theme.get('name', theme_name),
                'description': theme.get('description', ''),
                'colors': {
                    'bg': theme.get('bg'),
                    'text': theme.get('text'),
                    'water': theme.get('water'),
                    'parks': theme.get('parks'),
                    'road_motorway': theme.get('road_motorway'),
                    'road_primary': theme.get('road_primary'),
                    'road_residential': theme.get('road_residential'),
                }
            })
        except Exception as e:
            print(f"Error loading theme {theme_name}: {e}")
            continue

    return jsonify(theme_data)


@app.route('/api/theme/<theme_id>', methods=['GET'])
def get_theme(theme_id):
    """Get detailed theme data"""
    try:
        safe_theme_id = secure_filename(theme_id)
        if not safe_theme_id:
            return jsonify({'error': 'Theme not found'}), 404

        if safe_theme_id not in get_available_themes():
            return jsonify({'error': 'Theme not found'}), 404

        theme = load_theme(safe_theme_id)
        return jsonify(theme)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/theme/create', methods=['POST'])
def create_theme():
    """Create a new custom theme"""
    try:
        if not request.is_json:
            return jsonify({'error': 'JSON body is required'}), 400

        theme_data = request.json or {}

        # Validate required fields
        if 'name' not in theme_data:
            return jsonify({'error': 'Theme name is required'}), 400

        theme_name = theme_data['name'].strip()
        theme_filename = secure_filename(theme_name.lower().replace(' ', '_'))
        if not theme_filename:
            return jsonify({'error': 'Theme name is invalid'}), 400

        try:
            theme_path = _safe_resolve(THEMES_DIR, f"{theme_filename}.json")
        except ValueError:
            return jsonify({'error': 'Theme name is invalid'}), 400

        # Save theme
        with open(theme_path, 'w') as f:
            json.dump(theme_data, f, indent=2)

        return jsonify({
            'success': True,
            'theme_id': theme_filename,
            'message': f'Theme "{theme_name}" created successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Geocode an address to coordinates"""
    try:
        from geopy.geocoders import Nominatim
        import time

        if not request.is_json:
            return jsonify({'error': 'JSON body is required'}), 400

        data = request.json or {}
        address = data.get('address', '').strip()

        if not address:
            return jsonify({'error': 'Address is required'}), 400

        # Geocode the address
        geolocator = Nominatim(user_agent="map_poster_gui")
        time.sleep(1)  # Rate limiting
        location = geolocator.geocode(address)

        if not location:
            return jsonify({'error': 'Address not found'}), 404

        # Extract city and country from address components
        address_parts = location.address.split(', ')
        city = None
        country = None

        # Try to find city and country in address
        if len(address_parts) >= 2:
            country = address_parts[-1]
            # City is usually one of the first parts
            for part in address_parts[:3]:
                if part and not part.isdigit():
                    city = part
                    break

        return jsonify({
            'success': True,
            'coordinates': {
                'lat': location.latitude,
                'lon': location.longitude
            },
            'address': location.address,
            'city': city,
            'country': country
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate():
    """Start poster generation"""
    try:
        if not request.is_json:
            return jsonify({'error': 'JSON body is required'}), 400

        data = request.json or {}

        city = data.get('city', '').strip()
        country = data.get('country', '').strip()
        theme_id = data.get('theme', 'feature_based')
        distance = int(data.get('distance', 10000))
        coordinates = data.get('coordinates')
        add_house_marker = data.get('add_house_marker', False)
        options = _normalize_options(data.get('options', {}))

        # Validate inputs
        if not city or not country:
            return jsonify({'error': 'City and country are required'}), 400

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Initialize status
        generation_status[job_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing...',
            'output_file': None,
            'error': None
        }

        # Start generation in background thread
        thread = threading.Thread(
            target=generate_poster_background,
            args=(job_id, city, country, theme_id, distance, coordinates, add_house_marker, options)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'job_id': job_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_poster_background(job_id, city, country, theme_id, distance, coordinates=None, add_house_marker=False, options=None):
    """Background task for poster generation"""
    try:
        # Update status
        generation_status[job_id] = {
            'status': 'geocoding',
            'progress': 10,
            'message': 'Looking up coordinates...',
            'output_file': None,
            'error': None
        }

        # Load theme
        import create_map_poster
        theme_data = load_theme(theme_id)
        create_map_poster.THEME = theme_data

        # Get coordinates (use provided coordinates or look them up)
        if coordinates:
            coords = (coordinates['lat'], coordinates['lon'])
        else:
            coords = get_coordinates(city, country)

        generation_status[job_id] = {
            'status': 'downloading',
            'progress': 30,
            'message': 'Downloading map data...',
            'output_file': None,
            'error': None
        }

        # Generate output filename
        from create_map_poster import generate_output_filename
        output_file = generate_output_filename(city, theme_id)

        # Create poster with house marker if requested
        create_poster_with_marker(city, country, coords, distance, output_file, add_house_marker, options)

        # Success
        generation_status[job_id] = {
            'status': 'complete',
            'progress': 100,
            'message': 'Poster generated successfully!',
            'output_file': output_file,
            'error': None
        }

    except Exception as e:
        generation_status[job_id] = {
            'status': 'error',
            'progress': 0,
            'message': 'Generation failed',
            'output_file': None,
            'error': str(e)
        }


def create_poster_with_marker(city, country, coords, distance, output_file, add_house_marker, options=None):
    """Create poster and optionally add a house marker"""
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    import create_map_poster

    # Create the base poster
    create_poster(city, country, coords, distance, output_file, options=options)

    # Add house marker if requested
    if add_house_marker:
        # Reopen the image and add the marker
        from PIL import Image, ImageDraw, ImageFont

        img = Image.open(output_file)
        draw = ImageDraw.Draw(img)

        # Calculate marker position (center of image)
        width, height = img.size
        marker_x = width // 2
        marker_y = height // 2

        # Draw house emoji/symbol
        # For a simple house marker, draw a house shape
        marker_size = 40
        half_size = marker_size // 2

        # House shape (triangle roof + square base)
        # Triangle (roof)
        roof_points = [
            (marker_x, marker_y - half_size),  # Top
            (marker_x - half_size, marker_y),  # Bottom left
            (marker_x + half_size, marker_y)   # Bottom right
        ]

        # Square (base)
        base_box = [
            marker_x - half_size * 0.7,
            marker_y,
            marker_x + half_size * 0.7,
            marker_y + half_size
        ]

        # Get theme for colors
        theme = create_map_poster.THEME
        marker_color = theme.get('text', '#FF0000')
        outline_color = theme.get('bg', '#FFFFFF')

        # Draw with outline for visibility
        draw.polygon(roof_points, fill=marker_color, outline=outline_color, width=3)
        draw.rectangle(base_box, fill=marker_color, outline=outline_color, width=3)

        # Save the modified image
        img.save(output_file)


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get generation status"""
    if job_id not in generation_status:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(generation_status[job_id])


@app.route('/api/poster/<path:filename>', methods=['GET'])
def download_poster(filename):
    """Download generated poster"""
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Poster not found'}), 404
    try:
        poster_path = _safe_resolve(POSTERS_DIR, safe_name)
    except ValueError:
        return jsonify({'error': 'Poster not found'}), 404

    if not poster_path.exists():
        return jsonify({'error': 'Poster not found'}), 404

    return send_file(poster_path, mimetype='image/png')


@app.route('/api/poster/thumbnail/<path:filename>', methods=['GET'])
def get_thumbnail(filename):
    """Get poster thumbnail"""
    from PIL import Image
    import io

    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Poster not found'}), 404
    try:
        poster_path = _safe_resolve(POSTERS_DIR, safe_name)
    except ValueError:
        return jsonify({'error': 'Poster not found'}), 404

    if not poster_path.exists():
        return jsonify({'error': 'Poster not found'}), 404

    # Create thumbnail
    img = Image.open(poster_path)
    img.thumbnail((400, 533))

    # Save to bytes
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    print("=" * 60)
    print("Map Poster Generator - Web Application")
    print("=" * 60)
    print("\nStarting server...")
    print("\nOpen your browser and navigate to:")
    print("  http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5001)
