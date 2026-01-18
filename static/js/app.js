// Map Poster Generator - Main App JavaScript

let themes = [];
let selectedTheme = null;
let currentJobId = null;
let currentCoordinates = null;
let savedLayerPresets = [];

const BUILTIN_LAYER_PRESETS = {
    buildings: {
        name: 'Buildings',
        description: 'Building footprints as subtle filled shapes.',
        settings: {
            tag_key: 'building',
            tag_value: '',
            mode: 'fill',
            color: '#8b8b8b',
            line_width: '0.3',
            zorder: '2.3'
        }
    },
    railways: {
        name: 'Railways',
        description: 'Rail lines for transit corridors and rail yards.',
        settings: {
            tag_key: 'railway',
            tag_value: 'rail',
            mode: 'line',
            color: '#5b5b5b',
            line_width: '0.6',
            zorder: '2.6'
        }
    },
    cafes: {
        name: 'Cafes',
        description: 'Cafe amenities as highlighted POIs.',
        settings: {
            tag_key: 'amenity',
            tag_value: 'cafe',
            mode: 'fill',
            color: '#d97706',
            line_width: '0.4',
            zorder: '3.0'
        }
    },
    schools: {
        name: 'Schools',
        description: 'Schools and campuses as highlighted POIs.',
        settings: {
            tag_key: 'amenity',
            tag_value: 'school',
            mode: 'fill',
            color: '#2563eb',
            line_width: '0.4',
            zorder: '3.0'
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadThemes();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Distance slider
    const distanceSlider = document.getElementById('distance');
    const distanceValue = document.getElementById('distance-value');

    distanceSlider.addEventListener('input', (e) => {
        distanceValue.textContent = e.target.value;
    });

    // Generate button
    document.getElementById('generate-btn').addEventListener('click', generatePoster);

    // Theme search
    document.getElementById('theme-search').addEventListener('input', (e) => {
        filterThemes(e.target.value);
    });

    // New poster button
    document.getElementById('new-poster-btn').addEventListener('click', () => {
        document.getElementById('poster-result').style.display = 'none';
        document.getElementById('generate-btn').disabled = false;
    });

    // Address lookup button
    document.getElementById('lookup-btn').addEventListener('click', lookupAddress);

    // Enter key on address field
    document.getElementById('address').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            lookupAddress();
        }
    });

    // Advanced settings toggles
    document.getElementById('road-colors-hierarchy').addEventListener('change', toggleRoadColorOverride);
    document.getElementById('road-widths-hierarchy').addEventListener('change', toggleRoadWidthOverride);
    document.getElementById('custom-layer-enabled').addEventListener('change', toggleCustomLayerFields);
    document.getElementById('custom-layer-preset').addEventListener('change', applyCustomLayerPreset);
    document.getElementById('reset-advanced-btn').addEventListener('click', resetAdvancedSettings);
    document.getElementById('save-custom-preset-btn').addEventListener('click', saveCustomLayerPreset);
    document.getElementById('delete-custom-preset-btn').addEventListener('click', deleteCustomLayerPreset);
    document.getElementById('delete-all-presets-btn').addEventListener('click', deleteAllCustomLayerPresets);
    document.getElementById('export-presets-btn').addEventListener('click', exportCustomLayerPresets);
    document.getElementById('import-presets-btn').addEventListener('click', () => {
        document.getElementById('import-presets-input').click();
    });
    document.getElementById('import-presets-input').addEventListener('change', importCustomLayerPresets);
    const helpBtn = document.getElementById('custom-layer-help-btn');
    if (helpBtn) {
        helpBtn.addEventListener('click', toggleCustomLayerHelp);
    }

    loadCustomLayerPresets();
    toggleRoadColorOverride();
    toggleRoadWidthOverride();
    toggleCustomLayerFields();
    toggleCustomLayerHelp(true);
}

// Load themes from API
async function loadThemes() {
    try {
        const response = await fetch('/api/themes');
        themes = await response.json();

        renderThemes(themes);
    } catch (error) {
        console.error('Error loading themes:', error);
        document.getElementById('theme-grid').innerHTML =
            '<div class="loading">Error loading themes</div>';
    }
}

// Render themes in grid
function renderThemes(themesToRender) {
    const grid = document.getElementById('theme-grid');

    if (themesToRender.length === 0) {
        grid.innerHTML = '<div class="loading">No themes found</div>';
        return;
    }

    grid.innerHTML = themesToRender.map(theme => `
        <div class="theme-card" data-theme-id="${theme.id}">
            <h4>${theme.name}</h4>
            <p>${theme.description || 'Custom theme'}</p>
            <div class="theme-colors">
                <div class="theme-color-box" style="background: ${theme.colors.bg}"></div>
                <div class="theme-color-box" style="background: ${theme.colors.water}"></div>
                <div class="theme-color-box" style="background: ${theme.colors.parks}"></div>
                <div class="theme-color-box" style="background: ${theme.colors.road_motorway}"></div>
                <div class="theme-color-box" style="background: ${theme.colors.road_primary}"></div>
                <div class="theme-color-box" style="background: ${theme.colors.road_residential}"></div>
            </div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.theme-card').forEach(card => {
        card.addEventListener('click', () => selectTheme(card.dataset.themeId));
    });

    // Select first theme by default
    if (themesToRender.length > 0 && !selectedTheme) {
        selectTheme(themesToRender[0].id);
    }
}

// Filter themes by search
function filterThemes(query) {
    const filtered = themes.filter(theme =>
        theme.name.toLowerCase().includes(query.toLowerCase()) ||
        (theme.description && theme.description.toLowerCase().includes(query.toLowerCase()))
    );

    renderThemes(filtered);

    // Restore selection if still visible
    if (selectedTheme && filtered.find(t => t.id === selectedTheme)) {
        document.querySelector(`[data-theme-id="${selectedTheme}"]`)?.classList.add('selected');
        showThemePreview(selectedTheme);
    }
}

// Select a theme
async function selectTheme(themeId) {
    selectedTheme = themeId;

    // Update UI
    document.querySelectorAll('.theme-card').forEach(card => {
        card.classList.remove('selected');
    });

    document.querySelector(`[data-theme-id="${themeId}"]`)?.classList.add('selected');

    // Show preview
    await showThemePreview(themeId);
}

// Show theme preview
async function showThemePreview(themeId) {
    try {
        const response = await fetch(`/api/theme/${themeId}`);
        const theme = await response.json();

        const previewDiv = document.getElementById('theme-preview');
        const detailsDiv = document.getElementById('theme-details');

        // Draw preview canvas
        previewDiv.innerHTML = '<canvas id="theme-canvas" width="400" height="300"></canvas>';
        drawThemePreview(theme);

        // Show details
        document.getElementById('theme-name').textContent = theme.name;
        document.getElementById('theme-description').textContent = theme.description || '';

        // Color palette
        const paletteDiv = document.getElementById('color-palette');
        const colors = {
            'Background': theme.bg,
            'Text': theme.text,
            'Water': theme.water,
            'Parks': theme.parks,
            'Motorway': theme.road_motorway,
            'Primary': theme.road_primary,
            'Residential': theme.road_residential
        };

        paletteDiv.innerHTML = Object.entries(colors).map(([name, color]) => `
            <div class="color-item">
                <div class="color-swatch" style="background: ${color}"></div>
                <div class="color-info">
                    <span class="color-name">${name}</span>
                    <span class="color-hex">${color}</span>
                </div>
            </div>
        `).join('');

        detailsDiv.style.display = 'block';
    } catch (error) {
        console.error('Error loading theme preview:', error);
    }
}

// Draw theme preview on canvas
function drawThemePreview(theme) {
    const canvas = document.getElementById('theme-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Background
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0, 0, width, height);

    // Parks (rectangles)
    ctx.fillStyle = theme.parks;
    ctx.fillRect(40, 30, 80, 60);
    ctx.fillRect(240, 110, 100, 70);

    // Water (organic shape)
    ctx.fillStyle = theme.water;
    ctx.beginPath();
    ctx.ellipse(100, 200, 120, 80, 0, 0, Math.PI * 2);
    ctx.fill();

    // Roads
    // Motorway (thick)
    ctx.strokeStyle = theme.road_motorway;
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(0, 80);
    ctx.lineTo(width, 90);
    ctx.stroke();

    // Primary roads
    ctx.strokeStyle = theme.road_primary;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(100, 0);
    ctx.lineTo(100, height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(250, 0);
    ctx.lineTo(250, height);
    ctx.stroke();

    // Residential (thin)
    ctx.strokeStyle = theme.road_residential;
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(0, 150);
    ctx.lineTo(width, 150);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(200, 0);
    ctx.lineTo(200, height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(300, 0);
    ctx.lineTo(300, height);
    ctx.stroke();

    // Text
    ctx.fillStyle = theme.text;
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(theme.name, width / 2, height - 20);
}

// Generate poster
async function generatePoster() {
    const city = document.getElementById('city').value.trim();
    const country = document.getElementById('country').value.trim();
    const distance = document.getElementById('distance').value;

    // Validation
    if (!city || !country) {
        alert('Please enter both city and country');
        return;
    }

    if (!selectedTheme) {
        alert('Please select a theme');
        return;
    }

    // Disable button and show progress
    document.getElementById('generate-btn').disabled = true;
    const progressContainer = document.getElementById('progress-container');
    progressContainer.style.display = 'block';

    updateProgress(0, 'Initializing...');

    try {
        // Get house marker setting
        const addHouseMarker = document.getElementById('house-marker').checked;

        // Start generation
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                city,
                country,
                theme: selectedTheme,
                distance: parseInt(distance),
                coordinates: currentCoordinates,
                add_house_marker: addHouseMarker,
                options: getAdvancedOptions()
            })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Generation failed');
        }

        currentJobId = result.job_id;

        // Poll for status
        pollStatus(currentJobId);

    } catch (error) {
        console.error('Error generating poster:', error);
        alert(`Error: ${error.message}`);
        document.getElementById('generate-btn').disabled = false;
        progressContainer.style.display = 'none';
    }
}

// Poll generation status
async function pollStatus(jobId) {
    try {
        const response = await fetch(`/api/status/${jobId}`);
        const status = await response.json();

        updateProgress(status.progress, status.message);

        if (status.status === 'complete') {
            // Show result
            showPosterResult(status.output_file);
        } else if (status.status === 'error') {
            throw new Error(status.error);
        } else {
            // Continue polling
            setTimeout(() => pollStatus(jobId), 1000);
        }
    } catch (error) {
        console.error('Error polling status:', error);
        alert(`Error: ${error.message}`);
        document.getElementById('generate-btn').disabled = false;
        document.getElementById('progress-container').style.display = 'none';
    }
}

// Update progress bar
function updateProgress(percent, message) {
    document.getElementById('progress-fill').style.width = `${percent}%`;
    document.getElementById('progress-message').textContent = message;
}

// Show poster result
function showPosterResult(filename) {
    // Hide progress
    document.getElementById('progress-container').style.display = 'none';

    // Show result
    const resultDiv = document.getElementById('poster-result');
    const posterImage = document.getElementById('poster-image');
    const downloadBtn = document.getElementById('download-btn');

    const thumbnailUrl = `/api/poster/thumbnail/${filename.split('/').pop()}`;
    const downloadUrl = `/api/poster/${filename.split('/').pop()}`;

    posterImage.src = thumbnailUrl;
    downloadBtn.href = downloadUrl;
    downloadBtn.download = filename.split('/').pop();

    resultDiv.style.display = 'block';

    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

function parseNumber(value, fallback) {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : fallback;
}

function toggleRoadColorOverride() {
    const useHierarchy = document.getElementById('road-colors-hierarchy').checked;
    document.getElementById('road-color').disabled = useHierarchy;
}

function toggleRoadWidthOverride() {
    const useHierarchy = document.getElementById('road-widths-hierarchy').checked;
    document.getElementById('road-width').disabled = useHierarchy;
}

function toggleCustomLayerFields() {
    const enabled = document.getElementById('custom-layer-enabled').checked;
    const fields = [
        'custom-layer-key',
        'custom-layer-value',
        'custom-layer-style',
        'custom-layer-color',
        'custom-layer-width',
        'custom-layer-zorder',
        'custom-layer-preset-name',
        'custom-layer-preset-desc-input',
        'save-custom-preset-btn',
        'delete-custom-preset-btn',
        'delete-all-presets-btn',
        'export-presets-btn',
        'import-presets-btn'
    ];
    fields.forEach((id) => {
        document.getElementById(id).disabled = !enabled;
    });
}

function applyCustomLayerPreset() {
    const presetValue = document.getElementById('custom-layer-preset').value;
    const presetInfo = getPresetByValue(presetValue);
    updatePresetDescription(presetInfo?.description);

    if (!presetInfo) {
        return;
    }

    document.getElementById('custom-layer-enabled').checked = true;
    document.getElementById('custom-layer-key').value = presetInfo.settings.tag_key;
    document.getElementById('custom-layer-value').value = presetInfo.settings.tag_value;
    document.getElementById('custom-layer-style').value = presetInfo.settings.mode;
    document.getElementById('custom-layer-color').value = presetInfo.settings.color;
    document.getElementById('custom-layer-width').value = presetInfo.settings.line_width;
    document.getElementById('custom-layer-zorder').value = presetInfo.settings.zorder;
    document.getElementById('custom-layer-preset-name').value = presetInfo.name;
    document.getElementById('custom-layer-preset-desc-input').value = presetInfo.description || '';

    toggleCustomLayerFields();
}

function updatePresetDescription(text) {
    const desc = document.getElementById('custom-layer-preset-desc');
    desc.textContent = text || '';
}

function setPresetStatus(message, type = '') {
    const status = document.getElementById('preset-status');
    status.textContent = message || '';
    status.classList.remove('success', 'error');
    if (type) {
        status.classList.add(type);
    }
}

function toggleCustomLayerHelp(forceHide = false) {
    const helpBox = document.getElementById('custom-layer-help');
    if (!helpBox) {
        return;
    }
    if (forceHide) {
        helpBox.classList.add('hidden-input');
        return;
    }
    helpBox.classList.toggle('hidden-input');
}

function getCustomLayerSettings() {
    return {
        tag_key: document.getElementById('custom-layer-key').value.trim(),
        tag_value: document.getElementById('custom-layer-value').value.trim(),
        mode: document.getElementById('custom-layer-style').value,
        color: document.getElementById('custom-layer-color').value,
        line_width: document.getElementById('custom-layer-width').value,
        zorder: document.getElementById('custom-layer-zorder').value
    };
}

function loadCustomLayerPresets() {
    try {
        const stored = JSON.parse(localStorage.getItem('customLayerPresets') || '[]');
        savedLayerPresets = Array.isArray(stored) ? stored : [];
    } catch (error) {
        savedLayerPresets = [];
    }

    renderPresetOptions();
    updatePresetDescription('');
    setPresetStatus('');
}

function renderPresetOptions() {
    const select = document.getElementById('custom-layer-preset');
    select.innerHTML = '';

    const customOption = document.createElement('option');
    customOption.value = '';
    customOption.textContent = 'Custom';
    select.appendChild(customOption);

    const builtInGroup = document.createElement('optgroup');
    builtInGroup.label = 'Built-in';
    Object.entries(BUILTIN_LAYER_PRESETS).forEach(([key, preset]) => {
        const option = document.createElement('option');
        option.value = `builtin:${key}`;
        option.textContent = preset.name;
        builtInGroup.appendChild(option);
    });
    select.appendChild(builtInGroup);

    if (savedLayerPresets.length > 0) {
        const savedGroup = document.createElement('optgroup');
        savedGroup.label = 'Saved';
        savedLayerPresets.forEach((preset) => {
            const option = document.createElement('option');
            option.value = `saved:${preset.name}`;
            option.textContent = preset.name;
            savedGroup.appendChild(option);
        });
        select.appendChild(savedGroup);
    }
}

function getPresetByValue(value) {
    if (!value) {
        return null;
    }
    if (value.startsWith('builtin:')) {
        const key = value.replace('builtin:', '');
        return BUILTIN_LAYER_PRESETS[key] || null;
    }
    if (value.startsWith('saved:')) {
        const name = value.replace('saved:', '');
        return savedLayerPresets.find((preset) => preset.name === name) || null;
    }
    return null;
}

function saveCustomLayerPreset() {
    if (!document.getElementById('custom-layer-enabled').checked) {
        setPresetStatus('Enable the custom layer before saving a preset.', 'error');
        return;
    }

    const name = document.getElementById('custom-layer-preset-name').value.trim();
    if (!name) {
        setPresetStatus('Please enter a preset name.', 'error');
        return;
    }

    const description = document.getElementById('custom-layer-preset-desc-input').value.trim();
    const settings = getCustomLayerSettings();
    if (!settings.tag_key) {
        setPresetStatus('Please provide a tag key for the preset.', 'error');
        return;
    }

    const existingIndex = savedLayerPresets.findIndex((preset) => preset.name === name);
    const savedPreset = {
        name,
        description,
        settings
    };

    if (existingIndex >= 0) {
        savedLayerPresets[existingIndex] = savedPreset;
    } else {
        savedLayerPresets.push(savedPreset);
    }

    localStorage.setItem('customLayerPresets', JSON.stringify(savedLayerPresets));
    renderPresetOptions();
    document.getElementById('custom-layer-preset').value = `saved:${name}`;
    updatePresetDescription(description);
    setPresetStatus(`Preset "${name}" saved.`, 'success');
}

function deleteCustomLayerPreset() {
    const selected = document.getElementById('custom-layer-preset').value;
    if (!selected.startsWith('saved:')) {
        setPresetStatus('Select a saved preset to delete.', 'error');
        return;
    }

    const name = selected.replace('saved:', '');
    const confirmDelete = confirm(`Delete preset "${name}"?`);
    if (!confirmDelete) {
        return;
    }

    savedLayerPresets = savedLayerPresets.filter((preset) => preset.name !== name);
    localStorage.setItem('customLayerPresets', JSON.stringify(savedLayerPresets));

    renderPresetOptions();
    document.getElementById('custom-layer-preset').value = '';
    updatePresetDescription('');
    setPresetStatus(`Preset "${name}" deleted.`, 'success');
}

function deleteAllCustomLayerPresets() {
    if (savedLayerPresets.length === 0) {
        setPresetStatus('No saved presets to delete.', 'error');
        return;
    }

    const confirmDelete = confirm('Delete all saved presets? This cannot be undone.');
    if (!confirmDelete) {
        return;
    }

    savedLayerPresets = [];
    localStorage.removeItem('customLayerPresets');
    renderPresetOptions();
    document.getElementById('custom-layer-preset').value = '';
    updatePresetDescription('');
    setPresetStatus('All saved presets deleted.', 'success');
}

function exportCustomLayerPresets() {
    if (savedLayerPresets.length === 0) {
        setPresetStatus('No saved presets to export.', 'error');
        return;
    }

    const payload = {
        version: 1,
        exported_at: new Date().toISOString(),
        presets: savedLayerPresets
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'maptoposter-layer-presets.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setPresetStatus('Presets exported.', 'success');
}

function importCustomLayerPresets(event) {
    const input = event.target;
    const file = input.files?.[0];
    if (!file) {
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        try {
            const data = JSON.parse(reader.result);
            if (!data || !Array.isArray(data.presets)) {
                throw new Error('Invalid preset file format.');
            }

            const mode = prompt('Import presets: type "merge" or "overwrite".', 'merge');
            if (!mode) {
                setPresetStatus('Import canceled.', 'error');
                return;
            }

            const normalizedMode = mode.trim().toLowerCase();
            if (!['merge', 'overwrite'].includes(normalizedMode)) {
                setPresetStatus('Import canceled. Use "merge" or "overwrite".', 'error');
                return;
            }

            const merged = normalizedMode === 'overwrite' ? [] : [...savedLayerPresets];
            data.presets.forEach((preset) => {
                if (!preset?.name || !preset?.settings?.tag_key) {
                    return;
                }
                const existingIndex = merged.findIndex((item) => item.name === preset.name);
                if (existingIndex >= 0) {
                    merged[existingIndex] = preset;
                } else {
                    merged.push(preset);
                }
            });

            savedLayerPresets = merged;
            localStorage.setItem('customLayerPresets', JSON.stringify(savedLayerPresets));
            renderPresetOptions();
            updatePresetDescription('');
            setPresetStatus(`Presets imported (${normalizedMode}).`, 'success');
        } catch (error) {
            setPresetStatus(`Failed to import presets: ${error.message}`, 'error');
        } finally {
            input.value = '';
        }
    };
    reader.readAsText(file);
}

function resetAdvancedSettings() {
    document.getElementById('road-colors-hierarchy').checked = true;
    document.getElementById('road-widths-hierarchy').checked = true;
    document.getElementById('road-color').value = '#333333';
    document.getElementById('road-width').value = '0.6';
    document.getElementById('network-drive').checked = true;
    document.getElementById('network-bike').checked = true;
    document.getElementById('network-walk').checked = true;
    document.getElementById('use-cache').checked = true;

    document.getElementById('show-water').checked = true;
    document.getElementById('show-parks').checked = true;
    document.getElementById('show-buildings').checked = false;
    document.getElementById('show-railways').checked = false;
    document.getElementById('show-gradients').checked = true;
    document.getElementById('building-color').value = '#999999';
    document.getElementById('railway-color').value = '#666666';
    document.getElementById('railway-width').value = '0.6';

    document.getElementById('custom-layer-enabled').checked = false;
    document.getElementById('custom-layer-preset').value = '';
    document.getElementById('custom-layer-preset-name').value = '';
    document.getElementById('custom-layer-preset-desc-input').value = '';
    document.getElementById('custom-layer-key').value = '';
    document.getElementById('custom-layer-value').value = '';
    document.getElementById('custom-layer-style').value = 'line';
    document.getElementById('custom-layer-color').value = '#333333';
    document.getElementById('custom-layer-width').value = '0.5';
    document.getElementById('custom-layer-zorder').value = '2.5';
    updatePresetDescription('');
    setPresetStatus('');
    document.getElementById('import-presets-input').value = '';

    document.getElementById('text-city-y').value = '0.14';
    document.getElementById('text-line-y').value = '0.125';
    document.getElementById('text-country-y').value = '0.10';
    document.getElementById('text-coords-y').value = '0.07';
    document.getElementById('text-attribution-y').value = '0.02';

    toggleRoadColorOverride();
    toggleRoadWidthOverride();
    toggleCustomLayerFields();
}

function getAdvancedOptions() {
    const useRoadColors = document.getElementById('road-colors-hierarchy').checked;
    const useRoadWidths = document.getElementById('road-widths-hierarchy').checked;
    const customLayerEnabled = document.getElementById('custom-layer-enabled').checked;

    const customLayers = [];
    if (customLayerEnabled) {
        const tagKey = document.getElementById('custom-layer-key').value.trim();
        if (tagKey) {
            customLayers.push({
                tag_key: tagKey,
                tag_value: document.getElementById('custom-layer-value').value.trim(),
                mode: document.getElementById('custom-layer-style').value,
                color: document.getElementById('custom-layer-color').value,
                line_width: parseNumber(document.getElementById('custom-layer-width').value, 0.5),
                zorder: parseNumber(document.getElementById('custom-layer-zorder').value, 2.5)
            });
        }
    }

    return {
        use_road_hierarchy_colors: useRoadColors,
        use_road_hierarchy_widths: useRoadWidths,
        road_color: document.getElementById('road-color').value,
        road_width: parseNumber(document.getElementById('road-width').value, 0.6),
        network_types: getSelectedNetworkTypes(),
        use_cache: document.getElementById('use-cache').checked,
        show_water: document.getElementById('show-water').checked,
        show_parks: document.getElementById('show-parks').checked,
        show_buildings: document.getElementById('show-buildings').checked,
        show_railways: document.getElementById('show-railways').checked,
        show_gradients: document.getElementById('show-gradients').checked,
        building_color: document.getElementById('building-color').value,
        railway_color: document.getElementById('railway-color').value,
        railway_width: parseNumber(document.getElementById('railway-width').value, 0.6),
        custom_layers: customLayers,
        typography_positions: {
            city_y: parseNumber(document.getElementById('text-city-y').value, 0.14),
            line_y: parseNumber(document.getElementById('text-line-y').value, 0.125),
            country_y: parseNumber(document.getElementById('text-country-y').value, 0.10),
            coords_y: parseNumber(document.getElementById('text-coords-y').value, 0.07),
            attribution_y: parseNumber(document.getElementById('text-attribution-y').value, 0.02)
        }
    };
}

function getSelectedNetworkTypes() {
    const drive = document.getElementById('network-drive').checked;
    const bike = document.getElementById('network-bike').checked;
    const walk = document.getElementById('network-walk').checked;

    if (drive && bike && walk) {
        return ['all'];
    }

    const types = [];
    if (drive) types.push('drive');
    if (bike) types.push('bike');
    if (walk) types.push('walk');
    return types;
}

// Address lookup function
async function lookupAddress() {
    const address = document.getElementById('address').value.trim();

    if (!address) {
        alert('Please enter an address');
        return;
    }

    const lookupBtn = document.getElementById('lookup-btn');
    lookupBtn.disabled = true;
    lookupBtn.textContent = 'Looking up...';

    try {
        const response = await fetch('/api/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Geocoding failed');
        }

        // Store coordinates
        currentCoordinates = result.coordinates;

        // Update display
        const coordsDisplay = document.getElementById('coordinates-display');
        const coordsText = document.getElementById('coords-text');

        coordsText.textContent = `Lat: ${result.coordinates.lat.toFixed(4)}, Lon: ${result.coordinates.lon.toFixed(4)}`;
        coordsDisplay.classList.remove('hidden');

        // Auto-fill city and country if available
        if (result.city) {
            document.getElementById('city').value = result.city;
        }
        if (result.country) {
            document.getElementById('country').value = result.country;
        }

    } catch (error) {
        console.error('Error looking up address:', error);
        alert(`Error: ${error.message}`);
    } finally {
        lookupBtn.disabled = false;
        lookupBtn.textContent = 'Lookup';
    }
}
