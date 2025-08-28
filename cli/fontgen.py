#!/usr/bin/env python3
"""
FontGen with Potrace - Better vectorization for TTF fonts
Uses potrace for superior bitmap-to-vector conversion
"""

import argparse
import os
import sys
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import json
import html

class FontGeneratorPotrace:
    def __init__(self, character_overrides_path=None):
        # Load configuration
        self.config = self.load_config()
        
        # Load character overrides if provided
        self.character_overrides = {}
        if character_overrides_path:
            self.character_overrides = self.load_character_overrides(character_overrides_path)
        
        # Template settings
        template_settings = self.config['font_generation']['template_settings']
        self.template_size = template_settings['template_size']
        self.grid_cols = template_settings['grid_cols']
        self.margin = template_settings['margin']
        
        # Build character list with their properties
        self.characters = []
        self.char_properties = {}
        
        char_sets = self.config['font_generation']['character_sets']
        for set_name, set_data in char_sets.items():
            for char in set_data['characters']:
                self.characters.append(char)
                
                # Check for individual scaling override
                individual_scaling = set_data.get('individual_scaling', {})
                scale_factor = individual_scaling.get(char, set_data['scale_factor'])
                
                # Check for individual positioning override
                individual_positioning = set_data.get('individual_positioning', {})
                baseline_offset = individual_positioning.get(char, set_data['baseline_offset'])
                
                # Default properties from config
                properties = {
                    'scale_factor': scale_factor,
                    'baseline_offset': baseline_offset,
                    'set': set_name
                }
                
                # Apply character-specific overrides if they exist
                if char in self.character_overrides:
                    overrides = self.character_overrides[char]
                    properties.update(overrides)
                    print(f"Applied overrides for '{char}': {overrides}")
                
                self.char_properties[char] = properties
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ config.json not found. Using default settings.")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config.json: {e}. Using default settings.")
            return self.get_default_config()
    
    def load_character_overrides(self, overrides_path):
        """Load character-specific overrides from JSON file"""
        try:
            with open(overrides_path, 'r') as f:
                overrides = json.load(f)
                print(f"✅ Loaded character overrides from {overrides_path}")
                return overrides
        except FileNotFoundError:
            print(f"⚠️ Character overrides file not found: {overrides_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing character overrides JSON: {e}")
            return {}
    
    def get_default_config(self):
        """Fallback default configuration"""
        return {
            "font_generation": {
                "template_settings": {"template_size": 100, "grid_cols": 13, "margin": 20},
                "character_sets": {
                    "uppercase": {"characters": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), "scale_factor": 4.0, "baseline_offset": 150},
                    "lowercase": {"characters": list("abcdefghijklmnopqrstuvwxyz"), "scale_factor": 3.2, "baseline_offset": 120},
                    "numbers": {"characters": list("0123456789"), "scale_factor": 3.8, "baseline_offset": 140},
                    "symbols": {"characters": list("!@#$%^&*()-_=+[]{}|\\;:\"'<>,./?`~"), "scale_factor": 3.5, "baseline_offset": 130}
                },
                "glyph_settings": {"width": 500, "left_bearing": 25, "right_bearing": 25, "space_width": 250},
                "potrace_settings": {"border_crop": 4, "contrast_enhancement": 3.0, "threshold": 140},
                "font_properties": {"em_units": 1000, "ascent": 800, "descent": 200}
            }
        }
    
    def generate_template_svg(self, output_path):
        """Generate SVG template with boxes for each character"""
        rows = (len(self.characters) + self.grid_cols - 1) // self.grid_cols
        
        width = self.grid_cols * (self.template_size + self.margin) + self.margin
        height = rows * (self.template_size + self.margin) + self.margin + 50
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        .char-label {{ font-family: Arial; font-size: 16px; text-anchor: middle; }}
        .char-box {{ fill: none; stroke: #333; stroke-width: 2; }}
        .title {{ font-family: Arial; font-size: 20px; text-anchor: middle; font-weight: bold; }}
    </style>
    
    <text x="{width//2}" y="30" class="title">Font Template - Draw your characters in the boxes below</text>
'''
        
        for i, char in enumerate(self.characters):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = col * (self.template_size + self.margin) + self.margin
            y = row * (self.template_size + self.margin) + self.margin + 50
            
            svg_content += f'    <rect x="{x}" y="{y}" width="{self.template_size}" height="{self.template_size}" class="char-box"/>\n'
            
            label_x = x + self.template_size // 2
            label_y = y - 5
            escaped_char = html.escape(char)
            svg_content += f'    <text x="{label_x}" y="{label_y}" class="char-label">{escaped_char}</text>\n'
        
        svg_content += '</svg>'
        
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        print(f"Template created: {output_path}")
    
    def generate_template_png(self, output_path):
        """Generate PNG template with boxes for each character"""
        # First generate SVG template
        svg_path = output_path.replace('.png', '.svg')
        self.generate_template_svg(svg_path)
        
        # Then convert to PNG
        self.svg_to_png(svg_path, output_path)
        
        # Clean up temporary SVG file
        try:
            os.remove(svg_path)
        except:
            pass
    
    def svg_to_png(self, svg_path, png_path):
        """Convert SVG template to PNG for better Procreate compatibility"""
        try:
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=300)
            print(f"PNG version created: {png_path}")
            print("This PNG version is optimized for Procreate import!")
        except ImportError:
            print("cairosvg not available. Use --format png to generate PNG directly.")
    
    def extract_characters_from_image(self, image_path, font_name):
        """Extract individual character images from filled template"""
        try:
            img = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"Error opening image: {e}")
            return False
        
        char_dir = Path(f"temp_files/{font_name}_characters")
        char_dir.mkdir(parents=True, exist_ok=True)
        
        rows = (len(self.characters) + self.grid_cols - 1) // self.grid_cols
        
        for i, char in enumerate(self.characters):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = col * (self.template_size + self.margin) + self.margin
            y = row * (self.template_size + self.margin) + self.margin + 50
            
            char_img = img.crop((x, y, x + self.template_size, y + self.template_size))
            
            char_path = char_dir / f"{ord(char):04d}.png"
            char_img.save(char_path)
        
        print(f"Character images extracted to: {char_dir}")
        return str(char_dir)
    
    def preprocess_for_potrace(self, char_dir):
        """Preprocess character images for optimal potrace results"""
        print("🔧 Preprocessing images for potrace...")
        
        processed_dir = Path(f"temp_files/{Path(char_dir).name}_potrace")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        char_files = list(Path(char_dir).glob("*.png"))
        
        for char_file in char_files:
            try:
                with Image.open(char_file) as img:
                    # Convert to grayscale
                    gray = img.convert('L')
                    
                    # Get settings from config
                    potrace_settings = self.config['font_generation']['potrace_settings']
                    
                    # Crop out border area to remove template box lines
                    width, height = gray.size
                    border_crop = potrace_settings['border_crop']
                    if width > border_crop*2 and height > border_crop*2:
                        gray = gray.crop((border_crop, border_crop, 
                                        width-border_crop, height-border_crop))
                    
                    # Enhance contrast significantly
                    enhancer = ImageEnhance.Contrast(gray)
                    high_contrast = enhancer.enhance(potrace_settings['contrast_enhancement'])
                    
                    # Apply aggressive threshold for clean black/white
                    threshold = potrace_settings['threshold']
                    bw_img = high_contrast.point(lambda x: 0 if x < threshold else 255, '1')
                    
                    # Save as PBM format (potrace's preferred input)
                    pbm_path = processed_dir / f"{char_file.stem}.pbm"
                    bw_img.save(pbm_path)
                    
            except Exception as e:
                print(f"Warning: Could not preprocess {char_file.name}: {e}")
        
        print(f"✅ Preprocessed {len(char_files)} images for potrace")
        return str(processed_dir)
    
    def potrace_to_svg(self, pbm_dir):
        """Convert PBM files to SVG using potrace"""
        print("🎨 Converting bitmaps to vectors with potrace...")
        
        svg_dir = Path(f"temp_files/{Path(pbm_dir).name}_svg")
        svg_dir.mkdir(parents=True, exist_ok=True)
        
        pbm_files = list(Path(pbm_dir).glob("*.pbm"))
        successful_conversions = 0
        
        for pbm_file in pbm_files:
            try:
                svg_output = svg_dir / f"{pbm_file.stem}.svg"
                
                # Run potrace with optimized settings for font creation
                result = subprocess.run([
                    'potrace',
                    str(pbm_file),
                    '-s',  # SVG output
                    '-o', str(svg_output),
                    '--tight',  # Remove whitespace
                    '--turnpolicy', 'minority',  # Better for text
                    '--alphamax', '1.0',  # Smoother curves
                    '--opttolerance', '0.2'  # Optimize paths
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and svg_output.exists():
                    successful_conversions += 1
                else:
                    print(f"Potrace failed for {pbm_file.name}: {result.stderr}")
                    
            except Exception as e:
                print(f"Error processing {pbm_file.name}: {e}")
        
        print(f"✅ Potrace converted {successful_conversions} characters to SVG")
        return str(svg_dir) if successful_conversions > 0 else None
    
    def create_fontforge_script_with_svg(self, svg_dir, font_name):
        """Create FontForge script that imports SVG files with character-specific scaling"""
        
        # Get configuration values
        font_props = self.config['font_generation']['font_properties']
        glyph_settings = self.config['font_generation']['glyph_settings']
        
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
font.os2_typolinegap = {font_props.get('typo_line_gap', 0)}
font.hhea_linegap = {font_props.get('line_gap', 0)}

# Character properties mapping
char_properties = {self.char_properties!r}

successful_chars = 0
svg_dir = "{svg_dir}"

for char, props in char_properties.items():
    unicode_val = ord(char)
    svg_path = os.path.join(svg_dir, f"{{unicode_val:04d}}.svg")
    
    if os.path.exists(svg_path):
        try:
            print(f"Processing '{{char}}' ({{props['set']}}) from SVG...")
            
            # Create glyph
            glyph = font.createChar(unicode_val)
            
            # Import SVG (much better than bitmap!)
            glyph.importOutlines(svg_path, ("removeoverlap", "correctdir"))
            
            # Scale and position using character-specific settings
            scale_factor = props['scale_factor']
            baseline_offset = props['baseline_offset']
            
            glyph.transform(psMat.scale(scale_factor, scale_factor))
            # Position character properly - move to baseline (Y=0) plus any offset
            # X=75 for left margin, Y calculation for proper baseline positioning
            y_position = baseline_offset
            glyph.transform(psMat.translate(75, y_position))
            
            # Clean up paths and remove any border artifacts
            glyph.removeOverlap()
            glyph.simplify(1.0, ("setstarttoextremum", "removesingletonpoints"))
            glyph.round()
            
            # Set metrics from config
            glyph.width = {glyph_settings['width']}
            glyph.left_side_bearing = {glyph_settings['left_bearing']}
            glyph.right_side_bearing = {glyph_settings['right_bearing']}
            
            successful_chars += 1
            print(f"  ✅ Successfully vectorized '{{char}}' (scale: {{scale_factor}}x)")
            
        except Exception as e:
            print(f"  ❌ Error with '{{char}}': {{e}}")
            # Create fallback empty glyph
            try:
                glyph = font.createChar(unicode_val)
                glyph.width = {glyph_settings['width']}
            except:
                pass

# Add space character
try:
    space_glyph = font.createChar(32)
    space_glyph.width = {glyph_settings['space_width']}
    print("Added space character")
except:
    pass

# Set metadata
font.copyright = "Generated by FontGen with Potrace"
font.version = "1.0"
font.weight = "Regular"

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
    elif size > 5000:
        print("✅ Font file size is good")
    else:
        print("⚠️  Font file is small but may work")
'''
        
        script_path = f"temp_files/{font_name}_potrace_script.py"
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
                    print(f"\n🎉 SUCCESS! Potrace TTF font created: {output_font}")
                    print("📋 Try installing this in Font Book - it should work much better!")
                    return True
                else:
                    print("❌ Font file was not created")
                    return False
            else:
                print(f"❌ FontForge failed with exit code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ FontForge timed out")
            return False
        except Exception as e:
            print(f"❌ Error running FontForge: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='FontGen with Potrace - Better TTF generation')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Template generation command
    template_parser = subparsers.add_parser('template', help='Generate template for drawing characters')
    template_parser.add_argument('--format', choices=['svg', 'png'], default='svg',
                               help='Template format (default: svg)')
    template_parser.add_argument('--output', '-o', default='font_template',
                               help='Output filename (without extension)')
    template_parser.add_argument('--convert-to-png', action='store_true',
                               help='Convert SVG template to PNG (useful for Procreate import)')
    
    # Font generation command
    font_parser = subparsers.add_parser('generate', help='Generate TTF font from filled template using potrace')
    font_parser.add_argument('image', help='Path to filled template image')
    font_parser.add_argument('--name', '-n', required=True,
                           help='Font name')
    font_parser.add_argument('--character-overrides', type=str,
                           help='Path to JSON file with character-specific overrides')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Pass character overrides path if provided for generate command
    character_overrides_path = None
    if args.command == 'generate' and hasattr(args, 'character_overrides') and args.character_overrides:
        character_overrides_path = args.character_overrides
    
    fontgen = FontGeneratorPotrace(character_overrides_path)
    
    if args.command == 'template':
        output_path = f"{args.output}.{args.format}"
        
        if args.format == 'svg':
            fontgen.generate_template_svg(output_path)
            
            if args.convert_to_png:
                png_path = f"{args.output}.png"
                fontgen.svg_to_png(output_path, png_path)
        else:
            fontgen.generate_template_png(output_path)
            
    elif args.command == 'generate':
        if not os.path.exists(args.image):
            print(f"Error: Image file '{args.image}' not found")
            return
        
        success = fontgen.generate_font_with_potrace(args.image, args.name)
        if not success:
            print("\n💡 If potrace TTF generation failed, you can still use:")
            print("   python simple_font_generator.py generate [image] --name [name]")
            print("   This creates a bitmap font sprite that works everywhere!")
            sys.exit(1)

if __name__ == '__main__':
    main()