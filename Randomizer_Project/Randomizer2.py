#!/usr/bin/env python
# coding: utf-8

import sys
import os
import random
import time
import pandas as pd
from pathlib import Path
import math
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext

def per_item_chance(total_chance, item_count):
    """Calculate per-item chance based on total chance and item count.
    This math took me way too long to figure out, but hey, it works!"""
    return 1 - math.pow(1 - total_chance, 1 / item_count)

def resource_path(relative_path):
    """Get the absolute path to a resource file, works for both script and PyInstaller bundle.
    It stores the stupid files in the dumbest places."""
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle - files are in some magical temp directory
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running from script
        return os.path.join(os.path.abspath("."), relative_path)

def load_csv_data(filename, column_names=None):
    """Load CSV data with fallback to resource path.
    First tries to find the file locally (because that's where sane people put files),
    then falls back to PyInstaller's weird temp directory."""
    local_path = Path(filename)
    
    if local_path.is_file():
        # Found it locally! Thank God
        if column_names:
            return pd.read_csv(local_path, header=None, names=column_names)
        else:
            return pd.read_csv(local_path)
    else:
        # Gotta go hunting in PyInstaller's secret lair
        csv_path = resource_path(filename)
        if column_names:
            return pd.read_csv(csv_path, header=None, names=column_names)
        else:
            return pd.read_csv(csv_path)

def calculate_rarity_thresholds(party_level, item_count):
    """Calculate rarity thresholds based on party level and item count.
   The Bullshit section. TLDR Higher level = better gear. Probably needs more balancing."""

    #God I hate statistics so much jeez louise.

    # Base percentages with party level adjustments - 2% better chance per level
    target_uncommon = min(0.50 + party_level * 0.02, 0.95)
    target_rare = min(0.25 + party_level * 0.02, 0.95)
    target_extremely_rare = min(0.10 + party_level * 0.01, 0.95)
    target_exotic = min(0.05 + party_level * 0.01, 0.95)
    
    # Convert to per-item probabilities
    p_uncommon = per_item_chance(target_uncommon, item_count)
    p_rare = per_item_chance(target_rare, item_count)
    p_extremely_rare = per_item_chance(target_extremely_rare, item_count)
    p_exotic = per_item_chance(target_exotic, item_count)
    
    # Convert to thresholds (multiply by 1000 because integers are easier to work with)
    # Also, this prevents Python from having decimal precision issues
    exotic_threshold = int(p_exotic * 1000)
    extremely_rare_threshold = exotic_threshold + int(p_extremely_rare * 1000)
    rare_threshold = extremely_rare_threshold + int(p_rare * 1000)
    uncommon_threshold = rare_threshold + int(p_uncommon * 1000)
    
    return {
        'exotic': exotic_threshold,
        'extremely_rare': extremely_rare_threshold,
        'rare': rare_threshold,
        'uncommon': uncommon_threshold
    }

def categorize_items_by_rarity(df):
    """Categorize items by rarity.
    Splits all the items into their respective rarity buckets so we can pick from them later."""
    return {
        'common': df[df['Rarity'] == 'Common'],
        'uncommon': df[df['Rarity'] == 'Uncommon'],
        'rare': df[df['Rarity'] == 'Rare'],
        'extremely_rare': df[df['Rarity'] == 'Extremely Rare'],
        'exotic': df[df['Rarity'] == 'Exotic']
    }

def generate_random_items(categorized_items, thresholds, item_count):
    """Generate random items based on rarity thresholds."""
    shop_list = []
    
    for _ in range(item_count):
        item_roll = random.randint(1, 1000)
        
        if item_roll <= thresholds['exotic']:
            random_row = categorized_items['exotic'].sample(1)
        elif item_roll <= thresholds['extremely_rare']:
            random_row = categorized_items['extremely_rare'].sample(1)
        elif item_roll <= thresholds['rare']:
            random_row = categorized_items['rare'].sample(1)
        elif item_roll <= thresholds['uncommon']:
            random_row = categorized_items['uncommon'].sample(1)
        else:
            random_row = categorized_items['common'].sample(1)
        
        shop_list.append(random_row.iloc[0])
    
    return shop_list

def format_output_line(row, columns, widths):
    """Format a row for output display.
    Makes everything line up nice and pretty in columns."""
    return " ".join(f"{str(row[col]):<{width}}" for col, width in zip(columns, widths))

def shopRandomizer(shop_type, item_count, party_level, output_text):
    """Main shop randomizer function."""
    thresholds = calculate_rarity_thresholds(party_level, item_count)
    
    # Shop configuration based on type
    shop_configs = {
        'r': {
            'filename': 'ranged_list.csv',
            'columns': ["Weapon Name", "Weight", "Value", "Requirement", "Range",
                       "Type", "Damage", "AP Cost", "RoF", "Mag Size",
                       "Ammo Type", "Rarity", "Tier", "Page #"],
            'widths': [30, 8, 8, 12, 8, 8, 12, 8, 14, 8, 18, 15, 6, 8],
            'sort_key': 'Weapon Name',
            'separator_length': 170
        },
        'm': {
            'filename': 'melee_list.csv',
            'columns': ["Weapon Name", "Weight", "Value", "Range (Yards)", "Damage",
                       "AP Cost", "Rarity", "Tier", "Page #"],
            'widths': [30, 8, 8, 14, 12, 8, 15, 6, 8],
            'sort_key': 'Weapon Name',
            'separator_length': 125
        },
        'e': {
            'filename': 'explosive_list.csv',
            'columns': ["Weapon Name", "Weight", "Value", "Range (Yards)", "Damage",
                       "AP Cost", "Rarity", "AoE", "Tier", "Page #"],  # Uses default column names
            'widths': [30, 8, 8, 14, 12, 8, 15, 6, 6, 8],
            'sort_key': 'Weapon Name',
            'separator_length': 130
        },
        'a': {
            'filename': 'armor_list.csv',
            'columns': ["Armor Name", "DT", "Weight", "Value", "Faction",
                       "Effect", "Rarity", "Type", "Page #"],
            'widths': [40, 4, 8, 8, 12, 35, 15, 20, 6],
            'sort_key': 'Armor Name',
            'separator_length': 120
        },
        'h': {
            'filename': 'healing_list.csv',
            'columns': ["Item Name", "Value", "Weight", "Duration", "Addiction", 
                       "Effect", "Rarity", "Page #"],
            'widths': [25, 6, 8, 10, 10, 35, 15, 6],
            'sort_key': 'Item Name',
            'separator_length': 120
        },
        'g': {
            'filename': 'general_list.csv',
            'columns': ["Item Name", "Weight", "Value", "Special Rules", "Rarity", "Page #"],
            'widths': [30, 8, 8, 60, 15, 8],
            'sort_key': 'Item Name',
            'separator_length': 120  # General items - the miscellaneous stuff
        },
        'c': {
            'filename': 'clothes_list.csv',
            'columns': ["Item Name", "Weight", "Value", "Special Rules", "Rarity", "Page #"],
            'widths': [45, 8, 8, 40, 15, 8],
            'sort_key': 'Item Name',
            'separator_length': 120  # Clothes - because fashion is important in the wasteland
        }
    }
    

    #Worst Case Scenario if someone somehow enters an unknown shop type.
    if shop_type not in shop_configs:
        output_text.insert(tk.END, f"Error: Unknown shop type '{shop_type}'\n")
        return
    
    config = shop_configs[shop_type]
    
    try:
        # Load CSV data - If this errors one more time I'm gonna cry.
        df = load_csv_data(config['filename'], config['columns'])
        
        # Print header - make it look pretty
        header_line = " ".join(f"{col:<{width}}" for col, width in zip(config['columns'], config['widths']))
        output_text.insert(tk.END, header_line + "\n")
        output_text.insert(tk.END, "-" * config['separator_length'] + "\n")
        
        # Categorize items by rarity
        categorized_items = categorize_items_by_rarity(df)
        
        # Generate random items
        shop_list = generate_random_items(categorized_items, thresholds, item_count)
        
        # Sort items alphabetically
        shop_list.sort(key=lambda x: x[config['sort_key']])
        
        # Print sorted list
        for row in shop_list:
            line = format_output_line(row, config['columns'], config['widths'])
            output_text.insert(tk.END, line + "\n")
        
        # Debug message - Idk it looks good and makes sure the numbers are real.
        output_text.insert(tk.END, f"\nShop contains {len(shop_list)} items total.\n")
        output_text.see(tk.END)
        
    except Exception as e:
        # Something went wrong - probably a missing file or bad data
        output_text.insert(tk.END, f"Error loading data: {str(e)}\n")

class RandomizerGUI:
    #Behold a real GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Deadtree Shop Randomizer V0.0")
        self.root.geometry("1200x800")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights makes the layout responsive
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Deadtree Shop Randomizer", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Shop Type Selection
        ttk.Label(main_frame, text="Shop Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.shop_type = tk.StringVar(value='r')
        shop_frame = ttk.Frame(main_frame)
        shop_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        shop_types = [
            ("Ranged Weapons (r)", 'r'),
            ("Melee Weapons (m)", 'm'),
            ("Explosives (e)", 'e'),
            ("Armor (a)", 'a'),
            ("Healing (h)", 'h'),
            ("General Items (g)", 'g'),
            ("Clothes (c)", 'c')
        ]
        
        # Create radio buttons for each shop type
        for text, value in shop_types:
            ttk.Radiobutton(shop_frame, text=text, variable=self.shop_type, value=value).pack(side=tk.LEFT, padx=5)
        
        # Item Count
        ttk.Label(main_frame, text="Number of Items:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.item_count = tk.StringVar(value='10')
        item_count_entry = ttk.Entry(main_frame, textvariable=self.item_count, width=10)
        item_count_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Party Level
        ttk.Label(main_frame, text="Party Level:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.party_level = tk.StringVar(value='1')
        party_level_entry = ttk.Entry(main_frame, textvariable=self.party_level, width=10)
        party_level_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Generate Button
        generate_btn = ttk.Button(main_frame, text="Generate Shop", command=self.generate_shop)
        generate_btn.grid(row=3, column=2, padx=10, pady=5)
        
        # Clear Button
        clear_btn = ttk.Button(main_frame, text="Clear Output", command=self.clear_output)
        clear_btn.grid(row=3, column=3, padx=10, pady=5)
        
        # Output Text Area
        output_frame = ttk.LabelFrame(main_frame, text="Generated Shop Items", padding="5")
        output_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # The text area itself. uses Courier font because it looks cool
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.NONE, font=('Courier', 9))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Welcome message - because every good app needs a friendly greeting
        welcome_text = """

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡆⠀⠀⢤⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠖⠉⠘⡇⠀⠀⡸⠙⢧⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⢤⡴⠋⣀⡤⠶⠛⠛⠛⠿⣥⡀⠀⠻⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡜⠁⡰⢋⣔⠜⠃⠀⢀⠀⠂⠤⡀⠠⣙⢦⡴⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠀⡞⠍⠙⢦⡀⠀⠀⠀⠁⠢⡀⠙⡄⠘⣟⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡅⡼⢸⠀⠀⠀⠱⠀⣀⠰⣄⠀⠈⢦⡈⠦⡈⠳⠶⢶⡎
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠁⠸⡀⢇⠀⢀⠀⢀⣉⣀⠉⠑⢠⠘⡦⣈⢩⡶⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠀⢠⣷⡈⠸⣾⡲⠉⠁⢉⣽⣦⠀⠠⣯⢻⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀⢸⠀⡑⠀⠛⢃⠀⠀⢮⠁⣹⡆⠀⢿⣾⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣀⡤⠤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠸⡄⡞⠀⠇⠀⢼⣧⠢⡀⢮⣾⣿⠇⠀⠠⡙⢲⠀⠀⠀
⠀⠀⠀⢀⡔⢟⡩⠐⠂⠀⠉⠑⠪⣗⢄⠀⠀⠀⠀⠀⢹⠂⠀⠈⢆⠀⠀⠀⠀⠉⠉⠁⠀⠘⣗⠴⠋⠀⠀⠀
⠀⠀⣴⠏⡰⠋⠀⢀⠀⠀⠀⠀⠠⢀⡱⣥⣠⠤⣤⣤⠋⢠⠀⠀⠀⢣⠀⠀⡏⠒⠒⠒⠒⠊⠉⠀⠀⠀⠀⠀
⠀⣸⠃⡜⠀⠀⠰⠁⠀⣠⠶⠐⠒⠒⡷⣿⠀⠀⠀⢈⢢⡈⠣⣀⡀⡜⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢰⡇⡸⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⣼⣌⣿⠀⠀⠀⠈⠒⠤⢩⠋⠁⠀⠈⠑⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠀⠃⠀⠀⠀⢠⠀⢱⠀⠀⠀⢰⡏⠃⠉⡀⠀⠀⠀⠀⢀⢨⠢⠤⠄⠀⢀⣭⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⠀⠀⠀⠀⠈⢆⠸⡄⠀⠀⠈⡇⠀⠀⢳⡀⠀⠀⠀⠀⠵⠲⠮⡒⣧⣞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⡀⡄⠀⠀⠀⠀⠈⠆⢹⠀⣠⠖⠇⠀⣰⠃⢈⡗⢲⠇⠀⢸⠖⢺⡉⠀⠀⠈⢢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⡥⢧⠀⠀⠀⠀⠀⡀⣸⣰⠋⠀⠀⡼⠁⢀⡞⠀⡞⠀⠀⢸⠀⠀⠉⠓⡦⠀⠘⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠫⣢⢀⣀⢀⢜⡴⢻⠇⠀⠀⣰⠃⠀⢸⠃⢰⠇⠀⠀⠀⠀⠀⠀⣼⠁⠀⠀⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡔⣴⠉⡍⠛⠀⢿⠁⠀⡟⠀⠀⠀⡟⠀⠀⢸⠀⣾⠀⠀⠀⢸⡀⠀⠀⢹⡀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠹⣫⡤⠵⠀⣸⣆⠅⢸⠁⠀⠀⠀⡇⠀⠀⠸⡄⣿⠀⠀⠀⠘⡇⠀⠀⠀⠳⢤⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠓⠦⠖⠊⠁⠉⠀⢼⠀⠀⠀⠀⢛⠤⠤⠦⠇⣿⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠋⠀⠀⠀⠀⠹⠤⢤⣀⣠⣬⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        
        
Welcome to the Deadtree Shop Randomizer!

This tool generates random shop inventories based on your selected parameters.
Select a shop type, enter the number of items and party level, then click "Generate Shop".

For questions or suggestions, contact archer_rules on Discord.

War. War never changes."""
        
        self.output_text.insert(tk.END, welcome_text + "\n\n")
        self.output_text.see(tk.END)
    
    def generate_shop(self):
        """Generate shop based on current parameters."""
        try:
            # Clear previous output
            self.output_text.delete(1.0, tk.END)
            
            # Get values
            shop_type = self.shop_type.get()
            item_count = int(self.item_count.get())
            party_level = int(self.party_level.get())
            
            # Validate inputs for Dumbass users
            if item_count <= 0:
                messagebox.showerror("Error", "Number of items must be greater than 0")
                return
            
            if party_level <= 0:
                messagebox.showerror("Error", "Party level must be greater than 0")
                return
            
            # Update status gives me a funny out later to say "Reduced load times"
            self.status_var.set("Generating shop...")
            time.sleep(0.5)
            self.root.update()
            
            # Generate shop
            shopRandomizer(shop_type, item_count, party_level, self.output_text)
            
            # Update status
            self.status_var.set("Shop generated successfully!")
            
        except ValueError as e:
            # User probably entered text instead of numbers
            messagebox.showerror("Error", "Please enter valid numbers for item count and party level")
            self.status_var.set("Error: Invalid input")
        except Exception as e:
            # I coded this as a fallback cause I saw someone else do it but if anyone manages to trip it I'm gonna scream.
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred")
    
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Output cleared")

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = RandomizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()





