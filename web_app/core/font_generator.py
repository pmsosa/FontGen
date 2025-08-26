"""
Core font generation functionality extracted from fontgen.py
"""

import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import xml.etree.ElementTree as ET


class FontGenerator:
    def __init__(self, config_path="config.json"):
        """Initialize font generator with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        self.char_properties = self._build_char_properties()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config if file not found
            return self._get_default_config()
    
    def _get_default_config(self):
        """Return default configuration"""
        return {
            "character_sets": {
                "uppercase": {
                    "characters": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                    "scale_factor": 4.0,
                    "baseline_offset": 150
                },
                "lowercase": {
                    "characters": list("abcdefghijklmnopqrstuvwxyz"),
                    "scale_factor": 2.8,
                    "baseline_offset": 120
                },
                "numbers": {
                    "characters": list("0123456789"),
                    "scale_factor": 3.8,
                    "baseline_offset": 140
                },
                "symbols": {
                    "characters": ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '[', ']', '{', '}', '|', '\\', ';', ':', '"', "'", '<', '>', ',', '.', '/', '?', '`', '~'],
                    "scale_factor": 3.5,
                    "baseline_offset": 130
                }
            },
            "glyph_settings": {
                "width": 500,
                "left_bearing": 25,
                "right_bearing": 25,
                "space_width": 1800
            },
            "potrace_settings": {
                "border_crop": 4,
                "contrast_enhancement": 3.0,
                "threshold": 140,
                "turnpolicy": "minority",
                "alphamax": 1.0,
                "opttolerance": 0.2
            },
            "font_properties": {
                "em_units": 1000,
                "ascent": 800,
                "descent": 200,
                "typo_ascent": 800,
                "typo_descent": -200
            },
            "template_generation": {
                "box_size": 80,
                "box_spacing": 10,
                "margin": 20
            }
        }
    
    def _build_char_properties(self):
        """Build character properties mapping from config"""
        char_properties = {}
        
        # Handle both old and new config structures
        character_sets = self.config.get('character_sets', {})
        if not character_sets and 'font_generation' in self.config:
            character_sets = self.config['font_generation'].get('character_sets', {})
        
        for char_set, props in character_sets.items():
            for char in props['characters']:
                char_properties[char] = {
                    'scale_factor': props['scale_factor'],
                    'baseline_offset': props['baseline_offset']
                }
        return char_properties
    
    def get_all_characters(self):
        """Get all characters from all character sets"""
        chars = []
        
        # Handle both old and new config structures
        character_sets = self.config.get('character_sets', {})
        if not character_sets and 'font_generation' in self.config:
            character_sets = self.config['font_generation'].get('character_sets', {})
        
        for char_set in character_sets.values():
            chars.extend(char_set['characters'])
        return chars
    
    def get_character_sets(self):
        """Get available character sets"""
        return {
            "English Basic": {
                "uppercase": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                "lowercase": list("abcdefghijklmnopqrstuvwxyz"),
                "numbers": list("0123456789"),
                "symbols": ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '[', ']', '{', '}', '|', '\\', ';', ':', '"', "'", '<', '>', ',', '.', '/', '?', '`', '~']
            },
            "Spanish Extensions": {
                "accented": ['á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ü', 'Ñ', '¿', '¡']
            }
        }
    
    def generate_template_svg(self, output_path, characters=None):
        """Generate SVG template with character boxes"""
        if characters is None:
            characters = self.get_all_characters()
        
        # Calculate grid dimensions
        chars_per_row = 13
        num_rows = (len(characters) + chars_per_row - 1) // chars_per_row
        
        # Template settings
        template_config = self.config['template_generation']
        box_size = template_config['box_size']
        box_spacing = template_config['box_spacing']
        margin = template_config['margin']
        
        # Calculate dimensions
        width = margin + (chars_per_row * (box_size + box_spacing)) - box_spacing + margin
        height = margin + (num_rows * (box_size + box_spacing)) - box_spacing + margin
        
        # Create SVG
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <style>
        .char-box {{ fill: white; stroke: black; stroke-width: 2; }}
        .char-label {{ font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; dominant-baseline: middle; }}
    </style>
    <rect width="{width}" height="{height}" fill="white"/>
'''
        
        # Add character boxes
        for i, char in enumerate(characters):
            row = i // chars_per_row
            col = i % chars_per_row
            
            x = margin + col * (box_size + box_spacing)
            y = margin + row * (box_size + box_spacing)
            
            # Escape special characters for XML
            display_char = char
            if char in ['<', '>', '&', '"', "'"]:
                display_char = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&#39;'}[char]
            
            svg_content += f'''
    <rect class="char-box" x="{x}" y="{y}" width="{box_size}" height="{box_size}"/>
    <text class="char-label" x="{x + box_size//2}" y="{y - 10}">{display_char}</text>
'''
        
        svg_content += '</svg>'
        
        # Write SVG file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return True
    
    def svg_to_png(self, svg_path, png_path, scale=4):
        """Convert SVG to high-resolution PNG"""
        try:
            import cairosvg
            
            # Read SVG to get dimensions
            tree = ET.parse(svg_path)
            root = tree.getroot()
            svg_width = float(root.get('width', 800))
            svg_height = float(root.get('height', 600))
            
            # Convert with high resolution
            cairosvg.svg2png(
                url=svg_path,
                write_to=png_path,
                output_width=int(svg_width * scale),
                output_height=int(svg_height * scale)
            )
            
            return True
        except Exception as e:
            print(f"Error converting SVG to PNG: {e}")
            return False
    
    def extract_characters_from_image(self, image_path, font_name):
        """Extract individual character images from filled template"""
        # Create output directory
        output_dir = f"temp_files/{font_name}_characters"
        os.makedirs(output_dir, exist_ok=True)
        
        # Load and process image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get template settings
        template_config = self.config.get('template_generation', {
            'box_size': 80,
            'box_spacing': 10,
            'margin': 20
        })
        box_size = template_config['box_size']
        box_spacing = template_config['box_spacing']
        margin = template_config['margin']
        chars_per_row = 13
        
        # Calculate scale factor if image was resized
        expected_width = margin + (chars_per_row * (box_size + box_spacing)) - box_spacing + margin
        scale_factor = img.width / expected_width
        
        # Extract characters
        characters = self.get_all_characters()
        extracted_files = []
        
        for i, char in enumerate(characters):
            row = i // chars_per_row
            col = i % chars_per_row
            
            # Calculate box position (scaled)
            x = int((margin + col * (box_size + box_spacing)) * scale_factor)
            y = int((margin + row * (box_size + box_spacing)) * scale_factor)
            scaled_box_size = int(box_size * scale_factor)
            
            # Extract character box
            char_img = img.crop((x, y, x + scaled_box_size, y + scaled_box_size))
            
            # Save character image
            safe_char = char.replace('/', 'slash').replace('\\', 'backslash').replace(':', 'colon')
            char_path = os.path.join(output_dir, f"{safe_char}.png")
            char_img.save(char_path)
            extracted_files.append(char_path)
        
        print(f"Character images extracted to: {output_dir}")
        return output_dir
    
    def preprocess_for_potrace(self, char_dir):
        """Preprocess character images for potrace conversion"""
        pbm_dir = char_dir.replace('_characters', '_pbm')
        os.makedirs(pbm_dir, exist_ok=True)
        
        potrace_config = self.config.get('potrace_settings', self.config.get('font_generation', {}).get('potrace_settings', {
            'border_crop': 4,
            'contrast_enhancement': 3.0,
            'threshold': 140,
            'turnpolicy': 'minority',
            'alphamax': 1.0,
            'opttolerance': 0.2
        }))
        border_crop = potrace_config['border_crop']
        contrast_factor = potrace_config['contrast_enhancement']
        threshold = potrace_config['threshold']
        
        processed_count = 0
        
        for char_file in Path(char_dir).glob('*.png'):
            try:
                # Load image
                img = Image.open(char_file)
                
                # Crop borders to remove template box lines
                width, height = img.size
                if width > border_crop * 2 and height > border_crop * 2:
                    img = img.crop((border_crop, border_crop, 
                                  width - border_crop, height - border_crop))
                
                # Convert to grayscale
                if img.mode != 'L':
                    img = img.convert('L')
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast_factor)
                
                # Apply threshold to create binary image
                img = img.point(lambda x: 0 if x < threshold else 255, mode='1')
                
                # Save as PBM (bitmap format that potrace likes)
                pbm_path = os.path.join(pbm_dir, f"{char_file.stem}.pbm")
                img.save(pbm_path)
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing {char_file.name}: {e}")
                continue
        
        print(f"✅ Preprocessed {processed_count} characters for potrace")
        return pbm_dir
    
    def potrace_to_svg(self, pbm_dir):
        """Convert PBM files to SVG using potrace"""
        svg_dir = pbm_dir.replace('_pbm', '_svg')
        os.makedirs(svg_dir, exist_ok=True)
        
        potrace_config = self.config.get('potrace_settings', self.config.get('font_generation', {}).get('potrace_settings', {
            'border_crop': 4,
            'contrast_enhancement': 3.0,
            'threshold': 140,
            'turnpolicy': 'minority',
            'alphamax': 1.0,
            'opttolerance': 0.2
        }))
        successful_conversions = 0
        
        for pbm_file in Path(pbm_dir).glob('*.pbm'):
            try:
                svg_path = os.path.join(svg_dir, f"{pbm_file.stem}.svg")
                
                # Run potrace with configured settings
                cmd = [
                    'potrace',
                    '--svg',
                    '--output', svg_path,
                    '--turnpolicy', potrace_config['turnpolicy'],
                    '--alphamax', str(potrace_config['alphamax']),
                    '--opttolerance', str(potrace_config['opttolerance']),
                    str(pbm_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(svg_path):
                    successful_conversions += 1
                else:
                    print(f"Potrace failed for {pbm_file.name}: {result.stderr}")
                    
            except Exception as e:
                print(f"Error running potrace on {pbm_file.name}: {e}")
                continue
        
        print(f"✅ Potrace converted {successful_conversions} characters to SVG")
        return svg_dir if successful_conversions > 0 else None
    
    def update_config(self, new_settings):
        """Update configuration with new settings"""
        
        # Handle both old and new config structures
        character_sets_path = self.config.get('character_sets')
        if not character_sets_path and 'font_generation' in self.config:
            character_sets_path = self.config['font_generation'].get('character_sets', {})
            
        glyph_settings_path = self.config.get('glyph_settings')
        if not glyph_settings_path and 'font_generation' in self.config:
            glyph_settings_path = self.config['font_generation'].get('glyph_settings', {})
        
        # Update character set scaling
        if 'uppercase_scale' in new_settings and 'uppercase' in character_sets_path:
            character_sets_path['uppercase']['scale_factor'] = new_settings['uppercase_scale']
        if 'lowercase_scale' in new_settings and 'lowercase' in character_sets_path:
            character_sets_path['lowercase']['scale_factor'] = new_settings['lowercase_scale']
        if 'numbers_scale' in new_settings and 'numbers' in character_sets_path:
            character_sets_path['numbers']['scale_factor'] = new_settings['numbers_scale']
        if 'symbols_scale' in new_settings and 'symbols' in character_sets_path:
            character_sets_path['symbols']['scale_factor'] = new_settings['symbols_scale']
        
        # Update glyph settings
        if glyph_settings_path:
            if 'space_width' in new_settings:
                glyph_settings_path['space_width'] = new_settings['space_width']
            if 'left_bearing' in new_settings:
                glyph_settings_path['left_bearing'] = new_settings['left_bearing']
            if 'right_bearing' in new_settings:
                glyph_settings_path['right_bearing'] = new_settings['right_bearing']
        
        # Rebuild character properties
        self.char_properties = self._build_char_properties()
    
    def create_fontforge_script_with_svg(self, svg_dir, font_name):
        """Create FontForge script that imports SVG files with character-specific scaling"""
        
        # Get configuration values
        font_props = self.config.get('font_properties', self.config.get('font_generation', {}).get('font_properties', {
            'em_units': 1000,
            'ascent': 800,
            'descent': 200,
            'typo_ascent': 800,
            'typo_descent': -200
        }))
        glyph_settings = self.config.get('glyph_settings', self.config.get('font_generation', {}).get('glyph_settings', {
            'width': 500,
            'left_bearing': 25, 
            'right_bearing': 25,
            'space_width': 1800
        }))
        
        script_content = f'''#!/usr/bin/env fontforge

import fontforge
import os
import sys

# Create new font
font = fontforge.font()
font.fontname = "{font_name}"
font.familyname = "{font_name}"
font.fullname = "{font_name}"

# Set font properties from config
font.em = {font_props['em_units']}
font.ascent = {font_props['ascent']}
font.descent = {font_props['descent']}
font.os2_typoascent = {font_props.get('typo_ascent', font_props['ascent'])}
font.os2_typodescent = {font_props.get('typo_descent', -font_props['descent'])}

# Character properties mapping
char_properties = {self.char_properties!r}

successful_chars = 0
svg_directory = "{svg_dir}"

print(f"Processing SVG files from: {{svg_directory}}")

# Process each character
for svg_file in os.listdir(svg_directory):
    if not svg_file.endswith('.svg'):
        continue
    
    # Get character from filename
    char_name = svg_file.replace('.svg', '')
    
    # Handle special character names
    char_map = {{
        'slash': '/', 'backslash': '\\\\', 'colon': ':',
        'less': '<', 'greater': '>', 'question': '?',
        'quote': '"', 'apostrophe': "'"
    }}
    
    actual_char = char_map.get(char_name, char_name)
    
    if actual_char not in char_properties:
        print(f"Skipping unknown character: {{actual_char}}")
        continue
    
    try:
        # Create glyph
        glyph = font.createChar(ord(actual_char))
        
        # Get character-specific properties
        props = char_properties[actual_char]
        scale_factor = props['scale_factor']
        baseline_offset = props['baseline_offset']
        
        # Set glyph metrics
        glyph.width = {glyph_settings['width']}
        glyph.left_side_bearing = {glyph_settings['left_bearing']}
        glyph.right_side_bearing = {glyph_settings['right_bearing']}
        
        # Import SVG and scale
        svg_path = os.path.join(svg_directory, svg_file)
        glyph.importOutlines(svg_path)
        
        # Apply character-specific scaling and positioning
        if glyph.isWorthOutputting():
            # Transform: scale and position
            transform = fontforge.identity
            transform = fontforge.compose(transform, fontforge.scale(scale_factor))
            transform = fontforge.compose(transform, fontforge.translate(0, baseline_offset))
            glyph.transform(transform)
            
            successful_chars += 1
            print(f"✅ {{actual_char}}: scaled {{scale_factor}}x, baseline {{baseline_offset}}")
        else:
            print(f"⚠️  {{actual_char}}: empty or invalid SVG")
            
    except Exception as e:
        print(f"❌ {{actual_char}}: {{e}}")
        continue

# Add space character
space_glyph = font.createChar(ord(' '))
space_glyph.width = {glyph_settings['space_width']}

# Set font metadata
font.copyright = "Generated by FontGen with Potrace"
font.version = "1.0"

print(f"\\nSuccessfully processed {{successful_chars}} characters")

# Generate font
output_path = "{font_name}.ttf"
font.generate(output_path, flags=("opentype", "round"))

print(f"\\n🎉 Potrace font generated: {{output_path}}")

# Check file size
if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print(f"Font file size: {{size}} bytes")
    if size > 15000:
        print("✅ Font file size looks excellent!")
    else:
        print("⚠️  Font file seems small - check if characters imported correctly")
else:
    print("❌ Font file was not created")
    sys.exit(1)
'''
        
        # Write script file
        script_path = f"{font_name}_fontforge.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def generate_font_with_potrace(self, image_path, font_name):
        """Main function to generate TTF font using potrace pipeline"""
        print(f"🚀 Generating TTF font with potrace: '{font_name}'")
        
        # Check if FontForge is available
        try:
            subprocess.run(['fontforge', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ FontForge is required but not found!")
            print("Install with: brew install fontforge")
            return False
        
        # Step 1: Extract character images
        char_dir = self.extract_characters_from_image(image_path, font_name)
        if not char_dir:
            return False
        
        # Step 2: Preprocess for potrace
        pbm_dir = self.preprocess_for_potrace(char_dir)
        
        # Step 3: Convert to SVG with potrace
        svg_dir = self.potrace_to_svg(pbm_dir)
        if not svg_dir:
            print("❌ Potrace conversion failed")
            return False
        
        return svg_dir  # Return SVG directory for web preview
    
    def generate_final_font(self, svg_dir, font_name):
        """Generate final TTF font from SVG directory"""
        # Step 4: Create FontForge script
        script_path = self.create_fontforge_script_with_svg(svg_dir, font_name)
        
        # Step 5: Run FontForge
        try:
            print("🔨 Running FontForge with potrace vectors...")
            result = subprocess.run(['fontforge', '-script', script_path], 
                                  capture_output=True, text=True, timeout=300)
            
            print("FontForge output:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("Warnings:")
                print(result.stderr)
            
            if result.returncode == 0:
                output_font = f"{font_name}.ttf"
                if os.path.exists(output_font):
                    print(f"\n🎉 SUCCESS! TTF font created: {output_font}")
                    return output_font
                else:
                    print("❌ Font file was not created")
                    return None
            else:
                print(f"❌ FontForge failed with exit code {result.returncode}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ FontForge timed out")
            return None
        except Exception as e:
            print(f"❌ Error running FontForge: {e}")
            return None