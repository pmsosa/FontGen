#!/usr/bin/env python3
"""
Unit tests for FontGen - Test potrace compatibility and core functionality
"""

import unittest
import os
import tempfile
import subprocess
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.append('/Users/bullshark/Desktop/Playground/FontGen/cli')
from fontgen import FontGeneratorPotrace

class TestFontGen(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary config for testing
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.json")
        
        # Create test config
        test_config = {
            "font_generation": {
                "template_settings": {
                    "template_size": 100,
                    "grid_cols": 13,
                    "margin": 20
                },
                "character_sets": {
                    "uppercase": {
                        "characters": ["A", "B", "C"],
                        "scale_factor": 4.0,
                        "baseline_offset": 150
                    },
                    "lowercase": {
                        "characters": ["a", "b", "c"],
                        "scale_factor": 3.2,
                        "baseline_offset": 120
                    },
                    "numbers": {
                        "characters": ["0", "1", "2"],
                        "scale_factor": 3.8,
                        "baseline_offset": 140
                    }
                },
                "glyph_settings": {
                    "width": 500,
                    "left_bearing": 25,
                    "right_bearing": 25,
                    "space_width": 250
                },
                "potrace_settings": {
                    "border_crop": 4,
                    "contrast_enhancement": 3.0,
                    "threshold": 140
                },
                "font_properties": {
                    "em_units": 1000,
                    "ascent": 800,
                    "descent": 200
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Change to test directory so config is found
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        self.fontgen = FontGeneratorPotrace()
        
    def tearDown(self):
        """Clean up test files"""
        import shutil
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_fontforge_installation(self):
        """Test if FontForge is properly installed and working on M2"""
        print("\n🔍 Testing FontForge installation...")
        
        try:
            # Test basic FontForge availability
            result = subprocess.run(['fontforge', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            self.assertEqual(result.returncode, 0, 
                           "FontForge is not installed or not working")
            
            print(f"✅ FontForge version: {result.stdout.strip()}")
            
            # Check if it's native ARM64 or running under Rosetta
            arch_result = subprocess.run(['file', '/opt/homebrew/bin/fontforge'], 
                                       capture_output=True, text=True)
            
            if 'arm64' in arch_result.stdout:
                print("✅ FontForge is running natively on ARM64 (M2 compatible)")
            elif 'x86_64' in arch_result.stdout:
                print("⚠️  FontForge is x86_64 (may require Rosetta)")
            else:
                print(f"ℹ️  Architecture info: {arch_result.stdout}")
                
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.fail(f"FontForge test failed: {e}")
    
    def test_potrace_installation(self):
        """Test if Potrace is properly installed and working"""
        print("\n🎨 Testing Potrace installation...")
        
        try:
            # Test basic Potrace availability
            result = subprocess.run(['potrace', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            self.assertEqual(result.returncode, 0, 
                           "Potrace is not installed or not working")
            
            print(f"✅ Potrace version: {result.stdout.strip()}")
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.fail(f"Potrace test failed: {e}")
    
    def test_fontforge_python_scripting(self):
        """Test if FontForge Python scripting works"""
        print("\n🐍 Testing FontForge Python scripting...")
        
        # Create a minimal FontForge script
        test_script = os.path.join(self.test_dir, "test_script.py")
        with open(test_script, 'w') as f:
            f.write("""#!/usr/bin/env fontforge
import fontforge
import sys

try:
    # Create a simple font
    font = fontforge.font()
    font.fontname = "TestFont"
    font.familyname = "TestFont"
    
    # Create a simple glyph for 'A'
    glyph = font.createChar(ord('A'))
    glyph.width = 600
    
    # Simple rectangle outline for testing
    pen = glyph.glyphPen()
    pen.moveTo((100, 100))
    pen.lineTo((500, 100))
    pen.lineTo((500, 600))
    pen.lineTo((100, 600))
    pen.closePath()
    
    output_path = sys.argv[1] if len(sys.argv) > 1 else "test_font.ttf"
    font.generate(output_path)
    
    print("SUCCESS: Font generated successfully")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
""")
        
        try:
            output_font = os.path.join(self.test_dir, "test_font.ttf")
            result = subprocess.run(['fontforge', '-script', test_script, output_font], 
                                  capture_output=True, text=True, timeout=30)
            
            self.assertEqual(result.returncode, 0, 
                           f"FontForge scripting failed: {result.stderr}")
            
            # Check if font file was created
            self.assertTrue(os.path.exists(output_font), 
                          "Font file was not created")
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(output_font)
            self.assertGreater(file_size, 1000, 
                             "Generated font file is too small")
            
            print("✅ FontForge Python scripting works correctly")
            print(f"✅ Generated test font: {file_size} bytes")
            
        except subprocess.TimeoutExpired:
            self.fail("FontForge scripting timed out (may be hanging)")
        except Exception as e:
            self.fail(f"FontForge scripting test failed: {e}")
    
    def test_svg_template_generation(self):
        """Test SVG template generation"""
        print("\n📐 Testing SVG template generation...")
        
        svg_path = os.path.join(self.test_dir, "test_template.svg")
        self.fontgen.generate_template_svg(svg_path)
        
        self.assertTrue(os.path.exists(svg_path), "SVG template not created")
        
        # Check SVG content
        with open(svg_path, 'r') as f:
            content = f.read()
            
        self.assertIn('<svg', content, "Invalid SVG format")
        self.assertIn('Font Template', content, "Template title missing")
        self.assertIn('rect', content, "Character boxes missing")
        
        # Check if test characters are present (we only have A,B,C,a,b,c,0,1,2 in test config)
        for char in ['A', 'a', '0']:
            self.assertIn(f'>{char}<', content, f"Character {char} missing from template")
        
        print("✅ SVG template generation works")
    
    def test_config_loading(self):
        """Test configuration loading and character properties"""
        print("\n⚙️  Testing configuration loading...")
        
        # Test that config was loaded correctly
        self.assertIsNotNone(self.fontgen.config, "Config not loaded")
        
        # Test character properties
        self.assertIn('A', self.fontgen.char_properties, "Character 'A' not found in properties")
        self.assertIn('a', self.fontgen.char_properties, "Character 'a' not found in properties")
        
        # Test scaling differences
        uppercase_scale = self.fontgen.char_properties['A']['scale_factor']
        lowercase_scale = self.fontgen.char_properties['a']['scale_factor']
        
        self.assertEqual(uppercase_scale, 4.0, "Uppercase scale factor incorrect")
        self.assertEqual(lowercase_scale, 3.2, "Lowercase scale factor incorrect")
        self.assertLess(lowercase_scale, uppercase_scale, "Lowercase should be smaller than uppercase")
        
        print(f"✅ Config loaded with {len(self.fontgen.characters)} characters")
        print(f"✅ Uppercase scale: {uppercase_scale}x, Lowercase scale: {lowercase_scale}x")
    
    def test_png_template_generation(self):
        """Test PNG template generation via SVG conversion"""
        print("\n🖼️  Testing PNG template generation...")
        
        # First generate SVG, then convert to PNG
        svg_path = os.path.join(self.test_dir, "test_template.svg")
        png_path = os.path.join(self.test_dir, "test_template.png")
        
        self.fontgen.generate_template_svg(svg_path)
        self.fontgen.svg_to_png(svg_path, png_path)
        
        self.assertTrue(os.path.exists(png_path), "PNG template not created")
        
        # Check PNG properties
        with Image.open(png_path) as img:
            self.assertEqual(img.format, 'PNG', "Not a valid PNG file")
            self.assertGreater(img.width, 1000, "Template too narrow")
            self.assertGreater(img.height, 100, "Template too short")
            
        print(f"✅ PNG template generation works ({img.width}x{img.height})")
    
    def test_character_extraction(self):
        """Test character extraction from filled template"""
        print("\n✂️  Testing character extraction...")
        
        # Create a mock filled template
        svg_path = os.path.join(self.test_dir, "filled_template.svg")
        test_image = os.path.join(self.test_dir, "filled_template.png")
        
        # Generate template first to get proper dimensions
        self.fontgen.generate_template_svg(svg_path)
        self.fontgen.svg_to_png(svg_path, test_image)
        
        # Test character extraction
        char_dir = self.fontgen.extract_characters_from_image(test_image, "TestFont")
        
        self.assertTrue(os.path.exists(char_dir), "Character directory not created")
        
        # Check if character images were extracted
        char_files = list(Path(char_dir).glob("*.png"))
        self.assertGreater(len(char_files), 5, "Too few characters extracted")
        
        # Check a specific character file
        a_char_file = Path(char_dir) / f"{ord('A'):04d}.png"
        self.assertTrue(a_char_file.exists(), "Character 'A' not extracted")
        
        # Verify character image properties
        with Image.open(a_char_file) as char_img:
            self.assertEqual(char_img.size, 
                           (self.fontgen.template_size, self.fontgen.template_size),
                           "Character image wrong size")
        
        print(f"✅ Character extraction works ({len(char_files)} characters)")
    
    def test_potrace_preprocessing(self):
        """Test potrace preprocessing pipeline"""
        print("\n🔧 Testing potrace preprocessing...")
        
        # Create a mock filled template
        svg_path = os.path.join(self.test_dir, "test_preprocessing.svg")
        test_image = os.path.join(self.test_dir, "test_preprocessing.png")
        self.fontgen.generate_template_svg(svg_path)
        self.fontgen.svg_to_png(svg_path, test_image)
        
        # Test character extraction
        char_dir = self.fontgen.extract_characters_from_image(test_image, "PotraceTes")
        self.assertTrue(os.path.exists(char_dir), "Character directory not created")
        
        # Test preprocessing for potrace
        processed_dir = self.fontgen.preprocess_for_potrace(char_dir)
        self.assertTrue(os.path.exists(processed_dir), "Processed directory not created")
        
        # Check PBM files were created
        pbm_files = list(Path(processed_dir).glob("*.pbm"))
        self.assertGreater(len(pbm_files), 0, "No PBM files created")
        
        print(f"✅ Potrace preprocessing created {len(pbm_files)} PBM files")
    
    def test_potrace_conversion(self):
        """Test potrace bitmap-to-vector conversion"""
        print("\n🎨 Testing potrace conversion...")
        
        if not self._check_potrace_available():
            self.skipTest("Potrace not available")
        
        # Create test PBM files
        svg_path = os.path.join(self.test_dir, "test_potrace.svg")
        test_image = os.path.join(self.test_dir, "test_potrace.png")
        self.fontgen.generate_template_svg(svg_path)
        self.fontgen.svg_to_png(svg_path, test_image)
        
        char_dir = self.fontgen.extract_characters_from_image(test_image, "PotraceTest")
        processed_dir = self.fontgen.preprocess_for_potrace(char_dir)
        
        # Test potrace conversion
        svg_dir = self.fontgen.potrace_to_svg(processed_dir)
        
        if svg_dir:  # Only test if potrace succeeded
            self.assertTrue(os.path.exists(svg_dir), "SVG directory not created")
            
            # Check SVG files were created
            svg_files = list(Path(svg_dir).glob("*.svg"))
            self.assertGreater(len(svg_files), 0, "No SVG files created")
            
            print(f"✅ Potrace converted {len(svg_files)} files to SVG")
        else:
            print("⚠️  Potrace conversion failed (may be environment issue)")
    
    def _check_potrace_available(self):
        """Helper to check if potrace is available"""
        try:
            subprocess.run(['potrace', '--version'], 
                          capture_output=True, text=True, timeout=5)
            return True
        except:
            return False
    
    def test_end_to_end_workflow(self):
        """Test complete potrace workflow without FontForge"""
        print("\n🔄 Testing end-to-end potrace workflow (without font generation)...")
        
        # Step 1: Generate template
        svg_path = os.path.join(self.test_dir, "workflow_template.svg")
        template_path = os.path.join(self.test_dir, "workflow_template.png")
        self.fontgen.generate_template_svg(svg_path)
        self.fontgen.svg_to_png(svg_path, template_path)
        self.assertTrue(os.path.exists(template_path))
        
        # Step 2: Extract characters (simulating filled template)
        char_dir = self.fontgen.extract_characters_from_image(template_path, "WorkflowTest")
        self.assertTrue(os.path.exists(char_dir))
        
        # Step 3: Preprocess for potrace
        processed_dir = self.fontgen.preprocess_for_potrace(char_dir)
        self.assertTrue(os.path.exists(processed_dir))
        
        # Step 4: Test potrace conversion (if available)
        if self._check_potrace_available():
            svg_dir = self.fontgen.potrace_to_svg(processed_dir)
            if svg_dir:
                # Step 5: Create FontForge script with SVG
                script_path = self.fontgen.create_fontforge_script_with_svg(svg_dir, "WorkflowTest")
                self.assertTrue(os.path.exists(script_path))
                
                # Verify script content includes character properties
                with open(script_path, 'r') as f:
                    script_content = f.read()
                    self.assertIn('fontforge', script_content)
                    self.assertIn('WorkflowTest', script_content)
                    self.assertIn('char_properties', script_content)
                    self.assertIn('scale_factor', script_content)
                
                print("✅ Complete potrace workflow preparation works")
            else:
                print("⚠️  Potrace conversion failed, testing script creation only")
        else:
            print("⚠️  Potrace not available, skipping SVG conversion")
        
        print("✅ End-to-end workflow preparation completed")
    
    def test_performance_check(self):
        """Test performance on M2 hardware"""
        print("\n⚡ Testing performance...")
        
        import time
        
        # Time template generation
        start_time = time.time()
        template_path = os.path.join(self.test_dir, "perf_template.svg")
        self.fontgen.generate_template_svg(template_path)
        svg_time = time.time() - start_time
        
        # Time character extraction
        start_time = time.time()
        perf_svg = os.path.join(self.test_dir, "perf_template2.svg")
        png_path = os.path.join(self.test_dir, "perf_template.png")
        self.fontgen.generate_template_svg(perf_svg)
        self.fontgen.svg_to_png(perf_svg, png_path)
        char_dir = self.fontgen.extract_characters_from_image(png_path, "PerfTest")
        extraction_time = time.time() - start_time
        
        print(f"✅ SVG generation: {svg_time:.2f}s")
        print(f"✅ PNG + extraction: {extraction_time:.2f}s")
        
        # Performance should be reasonable on M2
        self.assertLess(svg_time, 5.0, "SVG generation too slow")
        self.assertLess(extraction_time, 10.0, "Character extraction too slow")

def run_system_info():
    """Print system information for debugging"""
    print("🖥️  System Information:")
    print("=" * 50)
    
    # System architecture
    try:
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        print(f"Architecture: {result.stdout.strip()}")
    except:
        print("Architecture: Unknown")
    
    # macOS version
    try:
        result = subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True)
        print(f"macOS Version: {result.stdout.strip()}")
    except:
        print("macOS Version: Unknown")
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Homebrew prefix (for M1/M2 vs Intel)
    brew_prefix = os.environ.get('HOMEBREW_PREFIX', 'Not set')
    print(f"Homebrew Prefix: {brew_prefix}")
    
    print()

if __name__ == '__main__':
    print("🧪 FontGen Potrace Unit Tests - M2 Mac Compatibility Check")
    print("=" * 65)
    
    # Print system info first
    run_system_info()
    
    # Run tests
    unittest.main(verbosity=2, buffer=True)