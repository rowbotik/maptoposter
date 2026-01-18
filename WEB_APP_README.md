# Map Poster Generator - Web Application

A modern, browser-based application for creating beautiful minimalist city map posters. Features a polished interface with live theme previews and a custom theme creator.

## Features

- **Modern Web Interface**: Clean, responsive design that works on any device
- **Live Theme Previews**: Visual canvas previews of each theme before generating
- **17+ Built-in Themes**: Professionally designed color schemes
- **Custom Theme Creator**: Visual theme editor with live preview
- **Real-time Progress**: See generation progress with status updates
- **Instant Preview**: View generated posters in the browser
- **Easy Download**: One-click poster download

## Installation

### 1. Install Dependencies

Make sure you have Python 3.8+ installed, then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Verify Fonts

Check that you have the Roboto fonts in the `fonts/` directory:
- Roboto-Bold.ttf
- Roboto-Regular.ttf
- Roboto-Light.ttf

## Running the Application

### Start the Server

```bash
python app.py
```

You'll see output like:

```
============================================================
Map Poster Generator - Web Application
============================================================

Starting server...

Open your browser and navigate to:
  http://localhost:5000

Press Ctrl+C to stop the server
============================================================
```

### Access the App

Open your web browser and go to:
```
http://localhost:5000
```

## Usage Guide

### Generating a Poster

1. **Enter Location**
   - Type your desired city name (e.g., "San Francisco")
   - Enter the country name (e.g., "USA")

2. **Adjust Map Radius**
   - Use the slider to set radius between 4km and 20km
   - Smaller radius = focused city center
   - Larger radius = wider metropolitan area

3. **Select a Theme**
   - Browse through the theme cards
   - Click any theme to see a live preview
   - View the full color palette for each theme

4. **Generate**
   - Click "Generate Poster"
   - Watch the real-time progress indicator
   - Preview and download your poster when complete

### Creating Custom Themes

1. **Navigate to Theme Creator**
   - Click "Theme Creator" in the navigation bar

2. **Design Your Theme**
   - Enter a name and description
   - Use the color pickers for each element
   - Click "Update Preview" to see changes
   - Adjust colors until satisfied

3. **Save Your Theme**
   - Click "Save Theme"
   - Your theme will be added to the theme list
   - Use it immediately in the generator

### Theme Elements Explained

- **Background**: Base color of the entire poster
- **Text**: Color for city name and labels
- **Gradient**: Fade effects at poster edges
- **Water**: Rivers, lakes, and water bodies
- **Parks**: Green spaces and park areas
- **Motorway**: Major highways (thickest roads)
- **Primary Roads**: Main city roads
- **Secondary Roads**: Secondary streets
- **Tertiary Roads**: Minor streets
- **Residential**: Neighborhood streets (thinnest roads)
- **Default Roads**: Fallback for uncategorized roads

## Tips for Best Results

### Map Radius Guidelines

| Distance | Best For | Examples |
|----------|----------|----------|
| 4-6km | Small/dense city centers | Venice, Amsterdam old center |
| 8-12km | Medium cities, downtown focus | Paris, Barcelona, San Francisco |
| 15-20km | Large metros, full city view | Tokyo, Mumbai, New York |

### Recommended Cities

**Iconic Grids**:
- New York, USA (12km) - Manhattan's famous street grid
- Barcelona, Spain (8km) - Eixample district grid pattern

**Waterfront & Canals**:
- Venice, Italy (4km) - Intricate canal network
- Amsterdam, Netherlands (6km) - Concentric canal rings
- Dubai, UAE (15km) - Palm Island and coastline

**Radial Patterns**:
- Paris, France (10km) - Haussmann boulevards
- Moscow, Russia (12km) - Ring road system

**River Cities**:
- London, UK (15km) - Thames River curves
- Budapest, Hungary (8km) - Danube split

### Theme Selection Tips

- **Noir**: Pure black & white - modern gallery aesthetic
- **Ocean**: Blue tones - perfect for coastal cities
- **Sunset**: Warm colors - great for evening mood
- **Blueprint**: Technical drawing style
- **Japanese Ink**: Minimalist Eastern aesthetic
- **Pastel Dream**: Soft, contemporary colors

## Technical Details

### Architecture

- **Backend**: Flask (Python web framework)
- **Frontend**: Vanilla JavaScript (no dependencies)
- **Styling**: Custom CSS with modern design system
- **Data**: OpenStreetMap via OSMnx
- **Geocoding**: Nominatim

### API Endpoints

- `GET /` - Main application page
- `GET /theme-creator` - Theme creator page
- `GET /api/themes` - List all themes with preview data
- `GET /api/theme/<id>` - Get detailed theme data
- `POST /api/theme/create` - Create new custom theme
- `POST /api/generate` - Start poster generation
- `GET /api/status/<job_id>` - Poll generation status
- `GET /api/poster/<filename>` - Download full poster
- `GET /api/poster/thumbnail/<filename>` - Get poster preview

### Output Specifications

- **Resolution**: 3600 x 4800 pixels
- **DPI**: 300 (print quality)
- **Format**: PNG
- **Location**: `posters/` directory
- **Naming**: `{city}_{theme}_{timestamp}.png`

## Troubleshooting

### Port Already in Use

If port 5000 is already taken, edit `app.py` and change the port:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Generation Timeout

If generation times out for large cities:
- Try a smaller map radius
- Check your internet connection
- The first generation may take longer due to data caching

### Theme Not Showing

After creating a custom theme:
- It should appear immediately in the theme list
- If not, click "Refresh Themes" or reload the page
- Check `themes/` directory to verify the JSON file was created

### Preview Not Loading

If poster preview doesn't show:
- Check that Pillow is installed: `pip install pillow`
- Verify the poster was created in `posters/` directory
- Check browser console for JavaScript errors

### Coordinate Lookup Fails

If city coordinates can't be found:
- Check spelling of city and country names
- Try more specific location (e.g., "San Francisco, California")
- Some small cities may not be in the database
- Wait a moment between requests (rate limiting)

## Development

### Running in Debug Mode

Debug mode is enabled by default during development:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

This enables:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use uWSGI:

```bash
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --wsgi-file app.py --callable app
```

### Customizing the Interface

**Colors**: Edit `static/css/style.css` - all colors are defined in CSS variables at the top

**Layout**: Modify templates in `templates/` directory

**Behavior**: Update JavaScript in `static/js/` directory

## Browser Compatibility

Tested and working on:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Performance

- Theme previews load instantly
- Generation time: 30 seconds - 2 minutes depending on city size
- Thumbnail generation: < 1 second
- UI remains responsive during generation (background processing)

## Credits

- Original CLI tool by originalankur
- Map data: OpenStreetMap contributors
- Web interface: Flask-based modern web application

## License

MIT License
