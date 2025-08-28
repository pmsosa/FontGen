#!/usr/bin/env python3
"""
Comprehensive test runner for FontGen
Runs all tests and provides a summary
"""

import os
import sys
import subprocess
import unittest
from pathlib import Path

def run_cli_tests():
    """Run CLI tests"""
    print("🖥️  Running CLI tests...")
    print("=" * 40)
    
    try:
        # Change to CLI test directory
        cli_test_dir = Path(__file__).parent / "cli"
        os.chdir(cli_test_dir)
        
        # Run CLI tests
        result = subprocess.run([
            sys.executable, "test_fontgen.py"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ CLI tests passed")
            return True
        else:
            print("❌ CLI tests failed")
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI tests timed out")
        return False
    except Exception as e:
        print(f"❌ CLI tests error: {e}")
        return False

def run_core_tests():
    """Run core functionality tests"""
    print("\n🧪 Running core functionality tests...")
    print("=" * 40)
    
    try:
        # Change to main test directory
        test_dir = Path(__file__).parent
        os.chdir(test_dir)
        
        # Run core tests
        result = subprocess.run([
            sys.executable, "test_core_functionality.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Core functionality tests passed")
            return True
        else:
            print("❌ Core functionality tests failed")
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Core functionality tests timed out")
        return False
    except Exception as e:
        print(f"❌ Core functionality tests error: {e}")
        return False

def run_web_tests():
    """Run web UI tests (if server is available)"""
    print("\n🌐 Running web UI tests...")
    print("=" * 40)
    
    try:
        # Change to web test directory
        web_test_dir = Path(__file__).parent / "webapp"
        os.chdir(web_test_dir)
        
        # Run web tests
        result = subprocess.run([
            sys.executable, "test_api.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Web UI tests passed")
            return True
        else:
            print("⚠️  Web UI tests failed (expected if server not running)")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Web UI tests timed out")
        return False
    except Exception as e:
        print(f"⚠️  Web UI tests error: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    print("=" * 40)
    
    dependencies = {
        'FontForge': 'fontforge --version',
        'Potrace': 'potrace --version',
        'Python PIL': f'{sys.executable} -c "from PIL import Image; print(\"PIL available\")"',
        'Python requests': f'{sys.executable} -c "import requests; print(\"requests available\")"'
    }
    
    results = {}
    
    for name, command in dependencies.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {name}: Available")
                results[name] = True
            else:
                print(f"❌ {name}: Not working")
                results[name] = False
        except FileNotFoundError:
            print(f"❌ {name}: Not installed")
            results[name] = False
        except subprocess.TimeoutExpired:
            print(f"⚠️  {name}: Timeout")
            results[name] = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results[name] = False
    
    return results

def main():
    """Main test runner"""
    print("🧪 FontGen Comprehensive Test Suite")
    print("=" * 50)
    
    # Check dependencies first
    deps = check_dependencies()
    
    # Run tests
    cli_result = run_cli_tests()
    core_result = run_core_tests()
    web_result = run_web_tests()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Dependencies: {'✅' if all(deps.values()) else '⚠️'}")
    print(f"   CLI Tests: {'✅' if cli_result else '❌'}")
    print(f"   Core Tests: {'✅' if core_result else '❌'}")
    print(f"   Web Tests: {'✅' if web_result else '⚠️'}")
    
    # Overall result
    critical_tests = cli_result and core_result
    if critical_tests:
        print("\n🎉 Critical tests passed! FontGen is ready for CI/CD.")
    else:
        print("\n💥 Critical tests failed! Fix issues before proceeding.")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not deps.get('FontForge', False):
        print("   - Install FontForge: brew install fontforge")
    if not deps.get('Potrace', False):
        print("   - Install Potrace: brew install potrace")
    if not cli_result:
        print("   - Fix CLI test failures")
    if not core_result:
        print("   - Fix core functionality test failures")
    if not web_result:
        print("   - Web tests require running server (optional for CI/CD)")
    
    return 0 if critical_tests else 1

if __name__ == '__main__':
    sys.exit(main())
