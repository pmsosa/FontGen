#!/usr/bin/env python3
"""
Debug tool to diagnose font generation issues
"""

import os
import sys
import subprocess
from PIL import Image
import tempfile

def check_character_images(char_dir):
    """Check if character images contain actual drawings"""
    print(f"🔍 Analyzing character images in {char_dir}...")
    
    if not os.path.exists(char_dir):
        print(f"❌ Directory {char_dir} not found")
        return False
    
    char_files = [f for f in os.listdir(char_dir) if f.endswith('.png')]
    print(f"Found {len(char_files)} character files")
    
    # Check a few sample characters
    samples = ['0065.png', '0097.png', '0048.png']  # A, a, 0
    
    for sample in samples:
        sample_path = os.path.join(char_dir, sample)
        if os.path.exists(sample_path):
            with Image.open(sample_path) as img:
                # Convert to grayscale and check if there's variation
                gray = img.convert('L')
                pixels = list(gray.getdata())
                
                # Check if image is mostly white (empty) or has content
                white_pixels = sum(1 for p in pixels if p > 240)
                total_pixels = len(pixels)
                white_ratio = white_pixels / total_pixels
                
                char_code = int(sample.replace('.png', ''))
                char = chr(char_code)
                
                print(f"  Character '{char}': {white_ratio:.1%} white pixels, size: {os.path.getsize(sample_path)} bytes")
                
                if white_ratio < 0.8:  # Less than 80% white = has content
                    print(f"    ✅ Has drawing content")
                else:
                    print(f"    ⚠️  Appears empty or very light")
    
    return True

def test_fontforge_with_sample(char_dir, font_name):
    """Test FontForge with detailed output"""
    print(f"\n🔧 Testing FontForge with sample characters...")
    
    # Create a minimal test script
    test_script = f"""#!/usr/bin/env fontforge

import fontforge
import os
import sys

print("Starting FontForge script...")

try:
    # Create new font
    font = fontforge.font()
    font.fontname = "{font_name}"
    font.familyname = "{font_name}"
    font.fullname = "{font_name}"
    
    # Set font properties
    font.em = 1000
    font.ascent = 800
    font.descent = 200
    
    print("Font created, processing characters...")
    
    # Test with just a few characters
    test_chars = [65, 97, 48]  # A, a, 0
    successful_chars = 0
    
    for unicode_val in test_chars:
        char = chr(unicode_val)
        img_path = os.path.join("{char_dir}", f"{{unicode_val:04d}}.png")
        
        if os.path.exists(img_path):
            print(f"Processing character '{{char}}' from {{img_path}}")
            
            try:
                # Create glyph
                glyph = font.createChar(unicode_val)
                
                # Import the image
                glyph.importOutlines(img_path)
                print(f"  Imported outlines for '{{char}}'")
                
                # Auto-trace the bitmap to vectors
                glyph.autoTrace()
                print(f"  Auto-traced '{{char}}'")
                
                # Set glyph width
                glyph.width = 600
                
                successful_chars += 1
                print(f"  ✅ Successfully processed '{{char}}'")
                
            except Exception as e:
                print(f"  ❌ Error processing '{{char}}': {{e}}")
        else:
            print(f"  ⚠️  Image not found: {{img_path}}")
    
    print(f"Successfully processed {{successful_chars}} characters")
    
    if successful_chars > 0:
        output_path = "{font_name}_debug.ttf"
        font.generate(output_path)
        print(f"✅ Font generated: {{output_path}}")
        
        # Check file size
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"Font file size: {{size}} bytes")
            if size < 5000:
                print("⚠️  Font file seems too small - may indicate issues")
            else:
                print("✅ Font file size looks reasonable")
        
    else:
        print("❌ No characters were successfully processed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FontForge error: {{e}}")
    sys.exit(1)

print("FontForge script completed successfully")
"""
    
    script_path = f"debug_{font_name}.py"
    with open(script_path, 'w') as f:
        f.write(test_script)
    
    # Run the debug script
    print("Running FontForge debug script...")
    try:
        result = subprocess.run(['fontforge', '-script', script_path], 
                              capture_output=True, text=True, timeout=60)
        
        print("FontForge stdout:")
        print(result.stdout)
        
        if result.stderr:
            print("FontForge stderr:")
            print(result.stderr)
        
        print(f"FontForge exit code: {result.returncode}")
        
        # Clean up
        if os.path.exists(script_path):
            os.remove(script_path)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ FontForge script timed out")
        return False
    except Exception as e:
        print(f"❌ Error running FontForge: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python debug_font.py <character_directory> <font_name>")
        print("Example: python debug_font.py SavasanaFont_characters SavasanaFont")
        sys.exit(1)
    
    char_dir = sys.argv[1]
    font_name = sys.argv[2]
    
    print("🐛 FontGen Debug Tool")
    print("=" * 40)
    
    # Check character images
    if not check_character_images(char_dir):
        return
    
    # Test FontForge
    if not test_fontforge_with_sample(char_dir, font_name):
        print("\n❌ FontForge test failed")
        return
    
    print(f"\n✅ Debug completed. Check {font_name}_debug.ttf")

if __name__ == '__main__':
    main()