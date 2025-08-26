#!/usr/bin/env python3
"""
Test the preview generation endpoint specifically
"""

import requests
import json
import os
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def create_test_image():
    """Create a simple test image with some text-like shapes"""
    img = Image.new('RGB', (800, 600), color='white')
    
    # Simple test - just save a white image for now
    test_path = "test_filled_template.png"
    img.save(test_path)
    return test_path

def test_preview_endpoint():
    """Test the preview generation step by step"""
    print("🧪 Testing Preview Generation...")
    print("=" * 40)
    
    # Step 1: Create and upload a test image
    print("📁 Creating test image...")
    test_image = create_test_image()
    
    try:
        print("📤 Uploading test image...")
        with open(test_image, 'rb') as f:
            files = {'file': ('test_template.png', f, 'image/png')}
            upload_response = requests.post(f"{BASE_URL}/api/upload-image", files=files, timeout=30)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Response: {upload_response.text}")
            return
        
        upload_result = upload_response.json()
        if not upload_result.get('success'):
            print(f"❌ Upload failed: {upload_result}")
            return
        
        file_path = upload_result['file_path']
        print(f"✅ Upload successful: {file_path}")
        
        # Step 2: Test preview generation
        print("\n🔮 Testing preview generation...")
        
        preview_data = {
            'file_path': file_path,
            'font_name': 'TestFont',
            'uppercase_scale': 4.0,
            'lowercase_scale': 2.8,
            'numbers_scale': 3.8,
            'symbols_scale': 3.5,
            'space_width': 1800,
            'left_bearing': 25,
            'right_bearing': 25
        }
        
        print(f"📋 Preview data: {preview_data}")
        
        try:
            preview_response = requests.post(
                f"{BASE_URL}/api/preview", 
                data=preview_data, 
                timeout=60  # Longer timeout for processing
            )
            
            print(f"📊 Preview response status: {preview_response.status_code}")
            
            if preview_response.status_code == 500:
                print("❌ Preview generation failed with 500 error")
                try:
                    error_detail = preview_response.json()
                    print(f"   Error detail: {error_detail}")
                except:
                    print(f"   Raw response: {preview_response.text}")
                return False
            elif preview_response.status_code == 200:
                result = preview_response.json()
                if result.get('success'):
                    print("✅ Preview generation successful!")
                    print(f"   SVG dir: {result.get('svg_dir')}")
                    print(f"   Character map entries: {len(result.get('character_map', {}))}")
                    return True
                else:
                    print(f"❌ Preview generation failed: {result}")
                    return False
            else:
                print(f"❌ Unexpected status code: {preview_response.status_code}")
                print(f"   Response: {preview_response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Preview generation timed out (>60s)")
            return False
        except Exception as e:
            print(f"❌ Preview generation error: {e}")
            return False
        
    finally:
        # Clean up test image
        if os.path.exists(test_image):
            os.remove(test_image)

def test_fontgen_directly():
    """Test FontGenerator class directly"""
    print("\n🔧 Testing FontGenerator directly...")
    
    try:
        import sys
        sys.path.append('.')
        from core.font_generator import FontGenerator
        
        # Test initialization
        font_gen = FontGenerator("../config.json")
        print("✅ FontGenerator initialized")
        
        # Test character extraction (this is likely where it fails)
        test_image = create_test_image()
        
        try:
            print("📸 Testing character extraction...")
            char_dir = font_gen.extract_characters_from_image(test_image, "TestFont")
            
            if char_dir and os.path.exists(char_dir):
                print(f"✅ Character extraction successful: {char_dir}")
                char_files = [f for f in os.listdir(char_dir) if f.endswith('.png')]
                print(f"   Extracted {len(char_files)} character files")
                
                # Test potrace preprocessing
                print("🔧 Testing potrace preprocessing...")
                pbm_dir = font_gen.preprocess_for_potrace(char_dir)
                
                if pbm_dir and os.path.exists(pbm_dir):
                    print(f"✅ Potrace preprocessing successful: {pbm_dir}")
                    pbm_files = [f for f in os.listdir(pbm_dir) if f.endswith('.pbm')]
                    print(f"   Created {len(pbm_files)} PBM files")
                    
                    # Test potrace conversion
                    print("🎨 Testing potrace conversion...")
                    svg_dir = font_gen.potrace_to_svg(pbm_dir)
                    
                    if svg_dir and os.path.exists(svg_dir):
                        print(f"✅ Potrace conversion successful: {svg_dir}")
                        svg_files = [f for f in os.listdir(svg_dir) if f.endswith('.svg')]
                        print(f"   Created {len(svg_files)} SVG files")
                        return True
                    else:
                        print("❌ Potrace conversion failed")
                        return False
                else:
                    print("❌ Potrace preprocessing failed")
                    return False
            else:
                print("❌ Character extraction failed")
                return False
                
        finally:
            if os.path.exists(test_image):
                os.remove(test_image)
            
    except Exception as e:
        print(f"❌ FontGenerator direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test FontGenerator directly first
    direct_test = test_fontgen_directly()
    
    if direct_test:
        print("\n" + "="*40)
        # Test via API
        api_test = test_preview_endpoint()
        
        if api_test:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ API test failed")
    else:
        print("\n❌ Direct FontGenerator test failed - API will likely fail too")