# Map Poster Generator - GUI Application

A beautiful desktop application for generating minimalist city map posters with customizable themes.

## Features

- **Intuitive Interface**: Simple point-and-click interface built with Python/Tkinter
- **17+ Built-in Themes**: Choose from professionally designed color schemes
- **Live Theme Previews**: See how themes look before generating
- **Custom Theme Creator**: Design and save your own color schemes with a visual editor
- **Progress Tracking**: Real-time feedback during poster generation
- **Poster Preview**: See your generated poster immediately in the app
- **Easy Export**: Save posters anywhere on your system

## Installation

1. Make sure you have Python 3.8+ installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify you have the required fonts in the `fonts/` directory:
   - Roboto-Bold.ttf
   - Roboto-Regular.ttf
   - Roboto-Light.ttf

## Usage

### Starting the Application

```bash
python map_poster_gui.py
```

### Generating a Poster

1. **Enter Location**:
   - City name (e.g., "San Francisco")
   - Country name (e.g., "USA")

2. **Adjust Map Radius**:
   - Use the slider to set the map radius (4,000m - 20,000m)
   - Smaller values = dense city center
   - Larger values = wider metropolitan view

3. **Select a Theme**:
   - Browse through the theme list
   - Click on any theme to see a live preview
   - View the color palette used in each theme

4. **Generate**:
   - Click "Generate Poster"
   - Wait for the progress bar to complete
   - View the preview and save to your desired location

### Creating Custom Themes

1. Click "Create Custom Theme" in the Theme section

2. In the Theme Creator dialog:
   - Enter a name and description for your theme
   - Adjust colors using the color pickers
   - Use "Update Preview" to see your changes
   - Click "Save Theme" to add it to your collection

3. Your custom theme will appear in the theme list

### Theme Color Guide

Each theme consists of these color elements:

- **Background**: Base color of the poster
- **Text**: City name and labels
- **Gradient**: Fade effects at top/bottom
- **Water**: Rivers, lakes, and water bodies
- **Parks**: Green spaces and parks
- **Road Hierarchy**:
  - Motorway: Major highways
  - Primary: Main roads
  - Secondary: Secondary streets
  - Tertiary: Minor streets
  - Residential: Neighborhood streets
  - Default: Fallback for other roads

## Tips for Best Results

### Map Radius Guidelines

- **4,000-6,000m**: Small/dense cities (Venice, Amsterdam old center)
- **8,000-12,000m**: Medium cities, downtown focus (Paris, Barcelona)
- **15,000-20,000m**: Large metros, full city view (Tokyo, Mumbai)

### City Recommendations

**Iconic Grids**:
- New York, USA (12,000m) - Manhattan grid
- Barcelona, Spain (8,000m) - Eixample district

**Waterfront Cities**:
- Venice, Italy (4,000m) - Canal network
- Amsterdam, Netherlands (6,000m) - Concentric canals
- Dubai, UAE (15,000m) - Palm & coastline

**Radial Patterns**:
- Paris, France (10,000m) - Haussmann boulevards
- Moscow, Russia (12,000m) - Ring roads

**River Cities**:
- London, UK (15,000m) - Thames curves
- Budapest, Hungary (8,000m) - Danube split

## Output

Posters are saved to the `posters/` directory with filenames in the format:
```
{city}_{theme}_{timestamp}.png
```

Resolution: 3600 x 4800 pixels (300 DPI)
Format: PNG

## Keyboard Shortcuts

- Enter (in city/country fields): Start generation
- Escape: Close dialogs

## Troubleshooting

**"Could not find coordinates"**:
- Check city and country spelling
- Try adding more detail (e.g., "San Francisco, California" instead of just "San Francisco")

**Slow generation**:
- Larger map radius = more data to download
- Complex cities with many roads take longer
- First generation may take longer due to caching

**Preview not showing**:
- Make sure Pillow is installed: `pip install pillow`
- Check that the poster file was created in `posters/` directory

**Fonts not loading**:
- Verify Roboto fonts exist in `fonts/` directory
- App will fall back to system fonts if Roboto is unavailable

## Technical Details

- Built with: Python 3.x, Tkinter
- Map data: OpenStreetMap (via OSMnx)
- Geocoding: Nominatim
- Rendering: Matplotlib

## Credits

Original command-line tool by originalankur
GUI wrapper adds desktop interface and custom theme creator

## License

MIT License
