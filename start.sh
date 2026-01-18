#!/bin/bash

# Map Poster Generator - Easy Start Script
# This script sets up a virtual environment and starts the web application

echo "============================================================"
echo "Map Poster Generator - Setup & Start"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv

    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "Installing dependencies..."
    pip install -r requirements.txt

    echo ""
    echo "Setup complete!"
    echo ""
else
    echo "Virtual environment already exists"
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "============================================================"
echo "Starting Map Poster Generator Web Application"
echo "============================================================"
echo ""
echo "The application will start in a moment..."
echo ""
echo "Open your browser and navigate to:"
echo "  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the Flask application
python app.py
