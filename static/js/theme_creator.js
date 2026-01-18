// Theme Creator JavaScript

// Color fields configuration
const colorFields = [
    { id: 'bg', label: 'Background' },
    { id: 'text', label: 'Text' },
    { id: 'gradient', label: 'Gradient' },
    { id: 'water', label: 'Water' },
    { id: 'parks', label: 'Parks' },
    { id: 'motorway', label: 'Motorway' },
    { id: 'primary', label: 'Primary Roads' },
    { id: 'secondary', label: 'Secondary Roads' },
    { id: 'tertiary', label: 'Tertiary Roads' },
    { id: 'residential', label: 'Residential' },
    { id: 'default', label: 'Default Roads' }
];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupColorPickers();
    setupEventListeners();
    updatePreview();
});

// Setup color pickers - sync between color input and hex input
function setupColorPickers() {
    colorFields.forEach(field => {
        const colorInput = document.getElementById(`color-${field.id}`);
        const hexInput = document.getElementById(`hex-${field.id}`);

        // Color picker changes hex input
        colorInput.addEventListener('input', (e) => {
            hexInput.value = e.target.value.toUpperCase();
        });

        // Hex input changes color picker
        hexInput.addEventListener('input', (e) => {
            const hex = e.target.value;
            if (/^#[0-9A-F]{6}$/i.test(hex)) {
                colorInput.value = hex;
            }
        });
    });
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('update-preview-btn').addEventListener('click', updatePreview);
    document.getElementById('save-theme-btn').addEventListener('click', saveTheme);
    document.getElementById('create-another-btn').addEventListener('click', resetForm);
}

// Update preview
function updatePreview() {
    const theme = getThemeData();
    drawThemePreview(theme);
    updateColorList(theme);
}

// Get theme data from form
function getThemeData() {
    const theme = {
        name: document.getElementById('theme-name').value || 'Custom Theme',
        description: document.getElementById('theme-desc').value || 'A custom theme'
    };

    // Get all colors
    const colorMapping = {
        'bg': 'bg',
        'text': 'text',
        'gradient': 'gradient_color',
        'water': 'water',
        'parks': 'parks',
        'motorway': 'road_motorway',
        'primary': 'road_primary',
        'secondary': 'road_secondary',
        'tertiary': 'road_tertiary',
        'residential': 'road_residential',
        'default': 'road_default'
    };

    Object.entries(colorMapping).forEach(([inputId, themeKey]) => {
        theme[themeKey] = document.getElementById(`color-${inputId}`).value;
    });

    return theme;
}

// Draw theme preview on canvas
function drawThemePreview(theme) {
    const canvas = document.getElementById('preview-canvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Background
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0, 0, width, height);

    // Parks (rectangles)
    ctx.fillStyle = theme.parks;
    ctx.fillRect(40, 30, 100, 80);
    ctx.fillRect(280, 130, 100, 90);

    // Water (organic shapes)
    ctx.fillStyle = theme.water;
    ctx.beginPath();
    ctx.ellipse(120, 220, 140, 70, 0, 0, Math.PI * 2);
    ctx.fill();

    // Roads with different hierarchy
    // Motorway (thickest)
    ctx.strokeStyle = theme.road_motorway;
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.moveTo(0, 90);
    ctx.lineTo(width, 100);
    ctx.stroke();

    // Primary roads
    ctx.strokeStyle = theme.road_primary;
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(120, 0);
    ctx.lineTo(120, height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(280, 0);
    ctx.lineTo(280, height);
    ctx.stroke();

    // Secondary roads
    ctx.strokeStyle = theme.road_secondary;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, 160);
    ctx.lineTo(width, 160);
    ctx.stroke();

    // Tertiary roads
    ctx.strokeStyle = theme.road_tertiary;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(200, 0);
    ctx.lineTo(200, height);
    ctx.stroke();

    // Residential (thinnest)
    ctx.strokeStyle = theme.road_residential;
    ctx.lineWidth = 1.5;

    ctx.beginPath();
    ctx.moveTo(0, 200);
    ctx.lineTo(width, 200);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(240, 0);
    ctx.lineTo(240, height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(340, 0);
    ctx.lineTo(340, height);
    ctx.stroke();

    // Text preview
    ctx.fillStyle = theme.text;
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(theme.name, width / 2, height - 20);
}

// Update color list below preview
function updateColorList(theme) {
    const container = document.getElementById('preview-colors');

    const displayColors = [
        { name: 'Background', key: 'bg' },
        { name: 'Text', key: 'text' },
        { name: 'Water', key: 'water' },
        { name: 'Parks', key: 'parks' },
        { name: 'Motorway', key: 'road_motorway' },
        { name: 'Primary', key: 'road_primary' },
        { name: 'Secondary', key: 'road_secondary' },
        { name: 'Tertiary', key: 'road_tertiary' },
        { name: 'Residential', key: 'road_residential' }
    ];

    container.innerHTML = displayColors.map(item => {
        const color = theme[item.key];
        return `
            <div style="display: inline-flex; align-items: center; margin: 0.5rem 1rem 0.5rem 0;">
                <div style="width: 30px; height: 30px; background: ${color}; border: 1px solid #ddd; border-radius: 4px; margin-right: 0.5rem;"></div>
                <span style="font-size: 0.875rem;">
                    <strong>${item.name}:</strong> ${color}
                </span>
            </div>
        `;
    }).join('');
}

// Save theme
async function saveTheme() {
    const theme = getThemeData();

    // Validation
    if (!theme.name || theme.name.trim() === '') {
        alert('Please enter a theme name');
        return;
    }

    try {
        const response = await fetch('/api/theme/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(theme)
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to save theme');
        }

        // Show success modal
        document.getElementById('success-modal').style.display = 'flex';

    } catch (error) {
        console.error('Error saving theme:', error);
        alert(`Error saving theme: ${error.message}`);
    }
}

// Reset form
function resetForm() {
    document.getElementById('theme-name').value = '';
    document.getElementById('theme-desc').value = '';

    // Reset colors to defaults
    const defaults = {
        'bg': '#FFFFFF',
        'text': '#000000',
        'gradient': '#FFFFFF',
        'water': '#C0C0C0',
        'parks': '#F0F0F0',
        'motorway': '#0A0A0A',
        'primary': '#1A1A1A',
        'secondary': '#2A2A2A',
        'tertiary': '#3A3A3A',
        'residential': '#4A4A4A',
        'default': '#3A3A3A'
    };

    Object.entries(defaults).forEach(([key, value]) => {
        document.getElementById(`color-${key}`).value = value;
        document.getElementById(`hex-${key}`).value = value;
    });

    // Hide modal
    document.getElementById('success-modal').style.display = 'none';

    // Update preview
    updatePreview();
}

// Preset themes for quick access
function loadPreset(presetName) {
    const presets = {
        'dark': {
            bg: '#000000',
            text: '#FFFFFF',
            gradient: '#000000',
            water: '#1a1a2e',
            parks: '#16213e',
            motorway: '#ffffff',
            primary: '#e0e0e0',
            secondary: '#b0b0b0',
            tertiary: '#808080',
            residential: '#505050',
            default: '#808080'
        },
        'ocean': {
            bg: '#f0f8ff',
            text: '#1e3a8a',
            gradient: '#f0f8ff',
            water: '#3b82f6',
            parks: '#86efac',
            motorway: '#1e40af',
            primary: '#3b82f6',
            secondary: '#60a5fa',
            tertiary: '#93c5fd',
            residential: '#bfdbfe',
            default: '#93c5fd'
        }
    };

    if (presets[presetName]) {
        const preset = presets[presetName];
        Object.entries(preset).forEach(([key, value]) => {
            document.getElementById(`color-${key}`).value = value;
            document.getElementById(`hex-${key}`).value = value;
        });
        updatePreview();
    }
}
