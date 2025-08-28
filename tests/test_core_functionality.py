#!/usr/bin/env python3
"""
Core functionality tests for FontGen
Tests the main classes and methods without requiring web server or external services
"""

import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cli'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'web_app'))

class TestCoreFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        
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
                    },
                    "symbols": {
                        "characters": ["!", "@", "#", "_", '"', "'"],
                        "scale_factor": 3.5,
                        "baseline_offset": 130,
                        "individual_scaling": {
                            "_": 2.0,
                            '"': 1.5,
                            "'": 1.5
                        },
                        "individual_positioning": {
                            "_": 20,
                            '"': 20,
                            "'": 20
                        }
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
        
        # Also create a main config.json in the test directory
        main_config_path = os.path.join(self.test_dir, "config.json")
        with open(main_config_path, 'w') as f:
            json.dump(test_config, f)
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Change to test directory so config is found
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test files"""
        import shutil
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_cli_fontgen_import(self):
        """Test that CLI FontGenerator can be imported and initialized"""
        print("\n🧪 Testing CLI FontGenerator import...")
        
        try:
            from fontgen import FontGeneratorPotrace
            fontgen = FontGeneratorPotrace(self.config_path)
            
            self.assertIsNotNone(fontgen.config)
            self.assertIsNotNone(fontgen.characters)
            self.assertIsNotNone(fontgen.char_properties)
            
            print(f"✅ CLI FontGenerator imported successfully")
            print(f"   Characters loaded: {len(fontgen.characters)}")
            print(f"   Character properties: {len(fontgen.char_properties)}")
            
        except ImportError as e:
            self.fail(f"Failed to import CLI FontGenerator: {e}")
        except Exception as e:
            self.fail(f"Failed to initialize CLI FontGenerator: {e}")
    
    def test_web_fontgenerator_import(self):
        """Test that Web FontGenerator can be imported and initialized"""
        print("\n🧪 Testing Web FontGenerator import...")
        
        try:
            from core.font_generator import FontGenerator
            fontgen = FontGenerator(self.config_path)
            
            self.assertIsNotNone(fontgen.config)
            self.assertIsNotNone(fontgen.char_properties)
            
            # Get characters using the method
            characters = fontgen.get_all_characters()
            self.assertIsNotNone(characters)
            
            print(f"✅ Web FontGenerator imported successfully")
            print(f"   Characters loaded: {len(characters)}")
            print(f"   Character properties: {len(fontgen.char_properties)}")
            
        except ImportError as e:
            self.fail(f"Failed to import Web FontGenerator: {e}")
        except Exception as e:
            self.fail(f"Failed to initialize Web FontGenerator: {e}")
    
    def test_svg_positioning_system(self):
        """Test the new SVG positioning system"""
        print("\n🧪 Testing SVG positioning system...")
        
        try:
            from fontgen import FontGeneratorPotrace
            fontgen = FontGeneratorPotrace(self.config_path)
            
            # Test that the method exists
            self.assertTrue(hasattr(fontgen, 'adjust_svg_positions'))
            
            # Test that special characters have positioning properties
            underscore_props = fontgen.char_properties.get('_')
            quote_props = fontgen.char_properties.get('"')
            
            self.assertIsNotNone(underscore_props)
            self.assertIsNotNone(quote_props)
            
            # Test that they have individual positioning
            self.assertIn('baseline_offset', underscore_props)
            self.assertIn('baseline_offset', quote_props)
            
            print(f"✅ SVG positioning system available")
            print(f"   Underscore baseline_offset: {underscore_props['baseline_offset']}")
            print(f"   Quote baseline_offset: {quote_props['baseline_offset']}")
            
        except Exception as e:
            self.fail(f"SVG positioning system test failed: {e}")
    
    def test_character_positioning_config(self):
        """Test that character positioning configuration is loaded correctly"""
        print("\n🧪 Testing character positioning configuration...")
        
        try:
            from fontgen import FontGeneratorPotrace
            fontgen = FontGeneratorPotrace(self.config_path)
            
            # Test that the config was loaded correctly
            self.assertIn('font_generation', fontgen.config)
            self.assertIn('character_sets', fontgen.config['font_generation'])
            self.assertIn('symbols', fontgen.config['font_generation']['character_sets'])
            
            symbols_set = fontgen.config['font_generation']['character_sets']['symbols']
            
            # Test that individual positioning and scaling are present
            self.assertIn('individual_positioning', symbols_set)
            self.assertIn('individual_scaling', symbols_set)
            
            positioning = symbols_set['individual_positioning']
            scaling = symbols_set['individual_scaling']
            
            # Test specific characters
            self.assertIn('_', positioning)
            self.assertIn('"', positioning)
            self.assertIn("'", positioning)
            
            self.assertIn('_', scaling)
            self.assertIn('"', scaling)
            self.assertIn("'", scaling)
            
            print(f"✅ Character positioning configuration loaded")
            print(f"   Underscore positioning: {positioning['_']}")
            print(f"   Quote positioning: {positioning['"']}")
            print(f"   Underscore scaling: {scaling['_']}")
            
        except Exception as e:
            self.fail(f"Character positioning configuration test failed: {e}")
    
    def test_template_generation(self):
        """Test template generation functionality"""
        print("\n🧪 Testing template generation...")
        
        try:
            from fontgen import FontGeneratorPotrace
            fontgen = FontGeneratorPotrace(self.config_path)
            
            # Test SVG template generation
            svg_path = os.path.join(self.test_dir, "test_template.svg")
            fontgen.generate_template_svg(svg_path)
            
            self.assertTrue(os.path.exists(svg_path))
            
            # Check SVG content
            with open(svg_path, 'r') as f:
                content = f.read()
                
            self.assertIn('<svg', content)
            self.assertIn('Font Template', content)
            
            print(f"✅ Template generation works")
            print(f"   SVG file created: {os.path.getsize(svg_path)} bytes")
            
        except Exception as e:
            self.fail(f"Template generation test failed: {e}")

def run_system_info():
    """Print system information for debugging"""
    print("🖥️  System Information:")
    print("=" * 50)
    
    # System architecture
    try:
        import platform
        print(f"Architecture: {platform.machine()}")
        print(f"Platform: {platform.platform()}")
    except:
        print("Architecture: Unknown")
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Current working directory
    print(f"Working Directory: {os.getcwd()}")
    
    print()

if __name__ == '__main__':
    print("🧪 FontGen Core Functionality Tests")
    print("=" * 50)
    
    # Print system info first
    run_system_info()
    
    # Run tests
    unittest.main(verbosity=2, buffer=True)
