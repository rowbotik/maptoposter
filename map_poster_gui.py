#!/usr/bin/env python3
"""
Map Poster GUI - Tkinter Desktop Application
Generates beautiful minimalist city map posters with theme customization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import threading
from pathlib import Path
from PIL import Image, ImageTk
import sys

# Import the main poster creation functions
from create_map_poster import (
    get_coordinates, create_poster, load_theme,
    get_available_themes, generate_output_filename
)

class ThemePreviewCanvas(tk.Canvas):
    """Canvas widget to display a visual preview of a theme's colors"""
    def __init__(self, parent, theme_data, **kwargs):
        super().__init__(parent, width=200, height=100, highlightthickness=1,
                         highlightbackground="#ccc", **kwargs)
        self.theme_data = theme_data
        self.draw_preview()

    def draw_preview(self):
        """Draw a simplified map preview using theme colors"""
        self.delete("all")

        # Background
        bg_color = self.theme_data.get('bg', '#FFFFFF')
        self.configure(bg=bg_color)

        # Parks (rectangles)
        parks_color = self.theme_data.get('parks', '#F0F0F0')
        self.create_rectangle(20, 15, 60, 45, fill=parks_color, outline="")
        self.create_rectangle(120, 55, 170, 85, fill=parks_color, outline="")

        # Water (rounded shape)
        water_color = self.theme_data.get('water', '#C0C0C0')
        self.create_oval(10, 50, 80, 95, fill=water_color, outline="")

        # Roads (lines with different widths)
        motorway_color = self.theme_data.get('road_motorway', '#000000')
        primary_color = self.theme_data.get('road_primary', '#1A1A1A')
        residential_color = self.theme_data.get('road_residential', '#4A4A4A')

        # Motorway (thick)
        self.create_line(0, 30, 200, 35, fill=motorway_color, width=3)
        # Primary roads
        self.create_line(50, 0, 50, 100, fill=primary_color, width=2)
        self.create_line(100, 0, 100, 100, fill=primary_color, width=2)
        # Residential (thin)
        self.create_line(0, 60, 200, 60, fill=residential_color, width=1)
        self.create_line(150, 0, 150, 100, fill=residential_color, width=1)

        # Text preview
        text_color = self.theme_data.get('text', '#000000')
        self.create_text(100, 90, text=self.theme_data.get('name', 'Theme'),
                        fill=text_color, font=('Arial', 8, 'bold'))


class ThemeCreatorDialog(tk.Toplevel):
    """Dialog window for creating/editing custom themes"""
    def __init__(self, parent, theme_data=None):
        super().__init__(parent)
        self.title("Custom Theme Creator")
        self.geometry("600x700")
        self.result = None

        # Default theme structure
        self.theme_data = theme_data or {
            "name": "Custom Theme",
            "description": "My custom theme",
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

        self.color_entries = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the theme creator UI"""
        # Main container with scrollbar
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Name and description
        ttk.Label(main_frame, text="Theme Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.insert(0, self.theme_data['name'])
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.desc_entry = ttk.Entry(main_frame, width=50)
        self.desc_entry.insert(0, self.theme_data.get('description', ''))
        self.desc_entry.pack(fill=tk.X, pady=(0, 20))

        # Color pickers
        colors_frame = ttk.LabelFrame(main_frame, text="Colors", padding="10")
        colors_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        color_labels = {
            'bg': 'Background',
            'text': 'Text',
            'gradient_color': 'Gradient',
            'water': 'Water',
            'parks': 'Parks/Green Spaces',
            'road_motorway': 'Motorways (main highways)',
            'road_primary': 'Primary Roads',
            'road_secondary': 'Secondary Roads',
            'road_tertiary': 'Tertiary Roads',
            'road_residential': 'Residential Streets',
            'road_default': 'Default Roads'
        }

        for key, label in color_labels.items():
            frame = ttk.Frame(colors_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)

            entry = ttk.Entry(frame, width=10)
            entry.insert(0, self.theme_data[key])
            entry.pack(side=tk.LEFT, padx=5)
            self.color_entries[key] = entry

            # Color preview box
            color_box = tk.Canvas(frame, width=30, height=20, bg=self.theme_data[key],
                                 highlightthickness=1, highlightbackground="#ccc")
            color_box.pack(side=tk.LEFT, padx=5)

            # Update preview when entry changes
            def update_preview(event, box=color_box, ent=entry):
                try:
                    color = ent.get()
                    box.configure(bg=color)
                except:
                    pass

            entry.bind('<KeyRelease>', update_preview)

            # Color picker button
            def pick_color(ent=entry, box=color_box):
                from tkinter import colorchooser
                color = colorchooser.askcolor(initialcolor=ent.get())[1]
                if color:
                    ent.delete(0, tk.END)
                    ent.insert(0, color)
                    box.configure(bg=color)

            ttk.Button(frame, text="Pick", width=8,
                      command=pick_color).pack(side=tk.LEFT)

        # Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Live Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 10))

        self.preview_canvas = None
        self.update_preview_btn = ttk.Button(preview_frame, text="Update Preview",
                                             command=self.update_preview)
        self.update_preview_btn.pack()

        self.preview_container = ttk.Frame(preview_frame)
        self.preview_container.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Save Theme",
                  command=self.save_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel",
                  command=self.destroy).pack(side=tk.LEFT)

        # Initial preview
        self.update_preview()

    def update_preview(self):
        """Update the theme preview"""
        # Get current theme data from entries
        current_theme = {
            'name': self.name_entry.get(),
            'description': self.desc_entry.get(),
        }
        for key, entry in self.color_entries.items():
            current_theme[key] = entry.get()

        # Clear old preview
        if self.preview_canvas:
            self.preview_canvas.destroy()

        # Create new preview
        self.preview_canvas = ThemePreviewCanvas(self.preview_container, current_theme)
        self.preview_canvas.pack()

    def save_theme(self):
        """Save the custom theme to a JSON file"""
        theme_name = self.name_entry.get().strip()
        if not theme_name:
            messagebox.showerror("Error", "Please enter a theme name")
            return

        # Build theme data
        theme = {
            'name': theme_name,
            'description': self.desc_entry.get().strip()
        }
        for key, entry in self.color_entries.items():
            theme[key] = entry.get().strip()

        # Save to themes directory
        theme_filename = theme_name.lower().replace(' ', '_')
        theme_path = Path('themes') / f"{theme_filename}.json"

        try:
            with open(theme_path, 'w') as f:
                json.dump(theme, f, indent=2)

            messagebox.showinfo("Success", f"Theme saved as '{theme_filename}'")
            self.result = theme_filename
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme: {e}")


class MapPosterGUI:
    """Main GUI application for Map Poster Generator"""
    def __init__(self, root):
        self.root = root
        self.root.title("Map Poster Generator")
        self.root.geometry("1000x800")

        # Global theme variable
        self.current_theme = None
        self.generated_poster_path = None

        self.setup_ui()
        self.load_themes()

    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        container = ttk.Frame(self.root, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Left panel - Controls
        left_panel = ttk.Frame(container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        # Title
        title_label = ttk.Label(left_panel, text="Map Poster Generator",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))

        # City Input
        input_frame = ttk.LabelFrame(left_panel, text="Location", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="City:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.city_entry = ttk.Entry(input_frame, width=30)
        self.city_entry.grid(row=0, column=1, pady=5)
        self.city_entry.insert(0, "San Francisco")

        ttk.Label(input_frame, text="Country:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.country_entry = ttk.Entry(input_frame, width=30)
        self.country_entry.grid(row=1, column=1, pady=5)
        self.country_entry.insert(0, "USA")

        # Distance slider
        ttk.Label(input_frame, text="Map Radius (meters):").grid(row=2, column=0,
                                                                  sticky=tk.W, pady=5)
        self.distance_var = tk.IntVar(value=10000)
        self.distance_label = ttk.Label(input_frame, text="10000m")
        self.distance_label.grid(row=2, column=1, sticky=tk.W, pady=5)

        distance_slider = ttk.Scale(input_frame, from_=4000, to=20000,
                                   variable=self.distance_var, orient=tk.HORIZONTAL,
                                   command=self.update_distance_label)
        distance_slider.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)

        # Theme Selection
        theme_frame = ttk.LabelFrame(left_panel, text="Theme", padding="10")
        theme_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Theme list with scrollbar
        list_container = ttk.Frame(theme_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.theme_listbox = tk.Listbox(list_container, height=15,
                                        yscrollcommand=scrollbar.set)
        self.theme_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.theme_listbox.yview)

        self.theme_listbox.bind('<<ListboxSelect>>', self.on_theme_select)

        # Theme buttons
        theme_btn_frame = ttk.Frame(theme_frame)
        theme_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(theme_btn_frame, text="Create Custom Theme",
                  command=self.open_theme_creator).pack(fill=tk.X, pady=2)
        ttk.Button(theme_btn_frame, text="Refresh Themes",
                  command=self.load_themes).pack(fill=tk.X, pady=2)

        # Generate Button
        self.generate_btn = ttk.Button(left_panel, text="Generate Poster",
                                       command=self.generate_poster,
                                       style='Accent.TButton')
        self.generate_btn.pack(fill=tk.X, pady=10)

        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(left_panel, textvariable=self.progress_var,
                                       font=('Arial', 9), foreground='#666')
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(left_panel, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Right panel - Preview
        right_panel = ttk.Frame(container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        preview_label = ttk.Label(right_panel, text="Theme Preview",
                                 font=('Arial', 14, 'bold'))
        preview_label.pack(pady=(0, 10))

        self.preview_frame = ttk.Frame(right_panel, relief=tk.RIDGE, borderwidth=2)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.preview_canvas = None

        # Poster preview label
        self.poster_preview_label = ttk.Label(right_panel, text="")
        self.poster_preview_label.pack()

        # Save button (initially hidden)
        self.save_btn = ttk.Button(right_panel, text="Save Poster As...",
                                   command=self.save_poster)

    def update_distance_label(self, value):
        """Update the distance label when slider moves"""
        distance = int(float(value))
        self.distance_label.config(text=f"{distance}m")
        self.distance_var.set(distance)

    def load_themes(self):
        """Load all available themes into the listbox"""
        self.theme_listbox.delete(0, tk.END)

        themes = get_available_themes()
        for theme in themes:
            self.theme_listbox.insert(tk.END, theme)

        # Select first theme
        if themes:
            self.theme_listbox.select_set(0)
            self.on_theme_select(None)

    def on_theme_select(self, event):
        """Handle theme selection"""
        selection = self.theme_listbox.curselection()
        if not selection:
            return

        theme_name = self.theme_listbox.get(selection[0])
        self.current_theme = theme_name

        # Load and display theme preview
        theme_data = load_theme(theme_name)

        # Clear old preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Show theme info
        info_frame = ttk.Frame(self.preview_frame, padding="10")
        info_frame.pack(fill=tk.X)

        ttk.Label(info_frame, text=theme_data.get('name', theme_name),
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        if 'description' in theme_data:
            desc_label = ttk.Label(info_frame, text=theme_data['description'],
                                  wraplength=400, foreground='#666')
            desc_label.pack(anchor=tk.W, pady=(5, 0))

        # Show preview canvas
        preview_canvas = ThemePreviewCanvas(self.preview_frame, theme_data)
        preview_canvas.pack(pady=20)

        # Color palette
        palette_frame = ttk.LabelFrame(self.preview_frame, text="Color Palette", padding="10")
        palette_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        colors = {
            'Background': theme_data.get('bg'),
            'Text': theme_data.get('text'),
            'Water': theme_data.get('water'),
            'Parks': theme_data.get('parks'),
            'Motorway': theme_data.get('road_motorway'),
            'Primary': theme_data.get('road_primary'),
            'Residential': theme_data.get('road_residential')
        }

        for i, (name, color) in enumerate(colors.items()):
            frame = ttk.Frame(palette_frame)
            frame.pack(fill=tk.X, pady=2)

            color_box = tk.Canvas(frame, width=40, height=20, bg=color,
                                 highlightthickness=1, highlightbackground="#ccc")
            color_box.pack(side=tk.LEFT, padx=(0, 10))

            ttk.Label(frame, text=f"{name}:").pack(side=tk.LEFT)
            ttk.Label(frame, text=color, font=('Courier', 9),
                     foreground='#666').pack(side=tk.LEFT, padx=5)

    def open_theme_creator(self):
        """Open the custom theme creator dialog"""
        dialog = ThemeCreatorDialog(self.root)
        self.root.wait_window(dialog)

        # Reload themes if a new one was created
        if dialog.result:
            self.load_themes()
            # Select the newly created theme
            themes = list(self.theme_listbox.get(0, tk.END))
            if dialog.result in themes:
                idx = themes.index(dialog.result)
                self.theme_listbox.select_clear(0, tk.END)
                self.theme_listbox.select_set(idx)
                self.theme_listbox.see(idx)
                self.on_theme_select(None)

    def generate_poster(self):
        """Generate the map poster in a background thread"""
        city = self.city_entry.get().strip()
        country = self.country_entry.get().strip()
        distance = self.distance_var.get()

        if not city or not country:
            messagebox.showerror("Error", "Please enter both city and country")
            return

        if not self.current_theme:
            messagebox.showerror("Error", "Please select a theme")
            return

        # Disable generate button
        self.generate_btn.config(state='disabled')
        self.progress_var.set("Generating poster...")
        self.progress_bar.start()

        # Hide poster preview
        self.poster_preview_label.config(image='', text='')
        self.save_btn.pack_forget()

        # Run generation in background thread
        thread = threading.Thread(target=self._generate_poster_thread,
                                 args=(city, country, distance))
        thread.daemon = True
        thread.start()

    def _generate_poster_thread(self, city, country, distance):
        """Background thread for poster generation"""
        try:
            # Load theme
            global THEME
            from create_map_poster import THEME as _THEME
            theme_data = load_theme(self.current_theme)

            # Monkey patch the THEME variable
            import create_map_poster
            create_map_poster.THEME = theme_data

            # Get coordinates
            self.root.after(0, lambda: self.progress_var.set("Looking up coordinates..."))
            coords = get_coordinates(city, country)

            # Generate poster
            self.root.after(0, lambda: self.progress_var.set("Downloading map data..."))
            output_file = generate_output_filename(city, self.current_theme)

            create_poster(city, country, coords, distance, output_file)

            # Success
            self.generated_poster_path = output_file
            self.root.after(0, lambda: self._on_generation_complete(output_file))

        except Exception as e:
            self.root.after(0, lambda: self._on_generation_error(str(e)))

    def _on_generation_complete(self, output_file):
        """Called when poster generation completes successfully"""
        self.progress_bar.stop()
        self.progress_var.set(f"✓ Poster saved: {os.path.basename(output_file)}")
        self.generate_btn.config(state='normal')

        # Load and display thumbnail
        try:
            img = Image.open(output_file)
            img.thumbnail((400, 533))  # Maintain aspect ratio
            photo = ImageTk.PhotoImage(img)

            self.poster_preview_label.config(image=photo, text='')
            self.poster_preview_label.image = photo  # Keep reference

            # Show save button
            self.save_btn.pack(pady=10)

        except Exception as e:
            self.poster_preview_label.config(text=f"Preview unavailable: {e}")

        messagebox.showinfo("Success", f"Poster generated successfully!\n\nSaved to: {output_file}")

    def _on_generation_error(self, error_msg):
        """Called when poster generation fails"""
        self.progress_bar.stop()
        self.progress_var.set("✗ Generation failed")
        self.generate_btn.config(state='normal')

        messagebox.showerror("Error", f"Failed to generate poster:\n\n{error_msg}")

    def save_poster(self):
        """Save the generated poster to a user-specified location"""
        if not self.generated_poster_path or not os.path.exists(self.generated_poster_path):
            messagebox.showerror("Error", "No poster to save")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=os.path.basename(self.generated_poster_path)
        )

        if filename:
            try:
                import shutil
                shutil.copy2(self.generated_poster_path, filename)
                messagebox.showinfo("Success", f"Poster saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save poster:\n{e}")


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    available_themes = style.theme_names()
    if 'aqua' in available_themes:  # macOS
        style.theme_use('aqua')
    elif 'clam' in available_themes:
        style.theme_use('clam')

    app = MapPosterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
