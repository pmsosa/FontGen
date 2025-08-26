#!/usr/bin/env python3
"""
Quick API tests for FontGen Web UI
Tests the main endpoints to identify issues
"""

import requests
import json
import os
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://127.0.0.1:8000"

def test_server_running():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not running: {e}")
        return False

def test_template_generation():
    """Test template generation endpoint"""
    print("\n🧪 Testing template generation...")
    
    try:
        # Test basic template generation
        data = {
            'characters': json.dumps(['A', 'B', 'C', 'a', 'b', 'c', '1', '2', '3']),
            'format': 'svg',
            'filename': 'test_template'
        }
        
        response = requests.post(f"{BASE_URL}/api/generate-template", data=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"❌ Template generation failed: {error_detail}")
                return False
            except:
                print(f"❌ Template generation failed: {response.text}")
                return False
        elif response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Template generation successful")
                print(f"   SVG file: {result.get('svg_file')}")
                return True
            else:
                print(f"❌ Template generation failed: {result}")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Template generation error: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing config loading...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/config", timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Config loaded successfully")
            
            # Check for required config sections
            required_sections = ['font_generation', 'character_sets', 'glyph_settings']
            missing_sections = []
            
            for section in required_sections:
                if section not in config and f'font_generation.{section}' not in str(config):
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"⚠️  Missing config sections: {missing_sections}")
            else:
                print("✅ All required config sections found")
                
            return True
        else:
            print(f"❌ Config loading failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_file_upload():
    """Test file upload endpoint"""
    print("\n🧪 Testing file upload...")
    
    # Create a dummy test image
    test_image_path = "test_image.png"
    
    try:
        # Create a simple test PNG file
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img.save(test_image_path)
        
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{BASE_URL}/api/upload-image", files=files, timeout=30)
        
        # Clean up test file
        os.remove(test_image_path)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ File upload successful")
                print(f"   File ID: {result.get('file_id')}")
                print(f"   File path: {result.get('file_path')}")
                return result.get('file_path')
            else:
                print(f"❌ File upload failed: {result}")
                return None
        else:
            print(f"❌ File upload failed: {response.status_code}")
            if response.status_code == 500:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ File upload error: {e}")
        # Clean up test file if it exists
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        return None

def test_fontgen_initialization():
    """Test if FontGenerator class can be initialized"""
    print("\n🧪 Testing FontGenerator initialization...")
    
    try:
        # Import the FontGenerator class
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from core.font_generator import FontGenerator
        
        # Try to initialize with the config file
        config_path = os.path.join("..", "config.json")
        font_gen = FontGenerator(config_path)
        
        # Test basic functionality
        chars = font_gen.get_all_characters()
        print(f"✅ FontGenerator initialized successfully")
        print(f"   Characters loaded: {len(chars)}")
        
        # Test character properties
        if hasattr(font_gen, 'char_properties') and font_gen.char_properties:
            print(f"   Character properties: {len(font_gen.char_properties)} entries")
        else:
            print("⚠️  No character properties found")
            
        return True
        
    except Exception as e:
        print(f"❌ FontGenerator initialization error: {e}")
        return False

def check_dependencies():
    """Check system dependencies"""
    print("\n🧪 Checking system dependencies...")
    
    import subprocess
    
    # Check FontForge
    try:
        result = subprocess.run(['fontforge', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FontForge found")
        else:
            print("❌ FontForge not working")
    except FileNotFoundError:
        print("❌ FontForge not installed")
    
    # Check Potrace
    try:
        result = subprocess.run(['potrace', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Potrace found")
        else:
            print("❌ Potrace not working")
    except FileNotFoundError:
        print("❌ Potrace not installed")
    
    # Check config file
    config_path = os.path.join("..", "config.json")
    if os.path.exists(config_path):
        print("✅ Config file found")
    else:
        print(f"❌ Config file not found at: {config_path}")

def main():
    print("🧪 FontGen Web UI API Tests")
    print("=" * 40)
    
    # Check dependencies first
    check_dependencies()
    
    # Test FontGenerator initialization
    fontgen_ok = test_fontgen_initialization()
    
    # Test if server is running
    if not test_server_running():
        print("\n❌ Server is not running. Start it with: ./startweb.sh")
        return
    
    # Run API tests
    config_ok = test_config_loading()
    template_ok = test_template_generation()
    upload_path = test_file_upload()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    print(f"   FontGenerator Init: {'✅' if fontgen_ok else '❌'}")
    print(f"   Config Loading: {'✅' if config_ok else '❌'}")
    print(f"   Template Generation: {'✅' if template_ok else '❌'}")
    print(f"   File Upload: {'✅' if upload_path else '❌'}")
    
    if not all([fontgen_ok, config_ok, template_ok, upload_path]):
        print("\n🔧 Issues found! Check the errors above.")
    else:
        print("\n🎉 All tests passed!")

if __name__ == "__main__":
    main()