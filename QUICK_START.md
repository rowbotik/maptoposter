# Quick Start Guide - Map Poster Generator Web App

Get started in 30 seconds!

## One-Command Start (macOS/Linux)

```bash
./start.sh
```

This will:
1. Create a virtual environment (if needed)
2. Install all dependencies
3. Start the web application

Then open your browser to: **http://localhost:5001**

## Manual Start (All Platforms)

### First Time Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Every Time You Run

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Start the app
python app.py
```

Then open: **http://localhost:5000**

## What You'll See

1. **Main Page**: Generator with theme selector
2. **Theme Creator**: Design custom themes
3. **Live Previews**: See themes before generating
4. **Progress Tracking**: Real-time generation updates

## Try It Out

1. Enter a city: "San Francisco"
2. Enter country: "USA"
3. Adjust the radius slider to 10km
4. Select a theme (try "Noir" or "Ocean")
5. Click "Generate Poster"
6. Wait 30-60 seconds
7. Download your poster!

## Creating Custom Themes

1. Click "Theme Creator" in the nav bar
2. Enter a theme name
3. Use color pickers to choose colors
4. Click "Update Preview" to see changes
5. Click "Save Theme"
6. Go back to Generator - your theme is now available!

## Troubleshooting

**Port already in use?**
- Edit `app.py`, change port 5000 to 5001

**Virtual environment issues?**
- Delete `venv` folder and run `./start.sh` again

**Generation fails?**
- Try a smaller city or different map radius
- Check your internet connection

## More Info

- Full documentation: `WEB_APP_README.md`
- Original CLI tool: `README.md`

## Stop the Server

Press `Ctrl+C` in the terminal

---

**Happy poster making!** 🗺️✨
