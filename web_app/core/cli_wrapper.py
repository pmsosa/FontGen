"""
CLI Wrapper for Web UI
Calls the CLI backend instead of duplicating font generation logic
"""

import os
import subprocess
import json
from typing import Optional, Dict, List


class CLIWrapper:
    """Wrapper around the CLI fontgen.py to avoid code duplication"""
    
    def __init__(self):
        # Get absolute path to CLI directory
        web_app_dir = os.path.dirname(os.path.dirname(__file__))
        self.cli_dir = os.path.abspath(os.path.join(web_app_dir, "..", "cli"))
        self.cli_script = os.path.join(self.cli_dir, "fontgen.py")
        self.config_path = os.path.join(self.cli_dir, "config.json")
        
        if not os.path.exists(self.cli_script):
            raise FileNotFoundError(f"CLI script not found at {self.cli_script}")
        
        # Load config for web UI features
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from CLI config.json"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _run_cli_command(self, args: List[str], timeout: int = 300) -> Dict:
        """Run a CLI command and return the result"""
        try:
            # Change to CLI directory
            original_dir = os.getcwd()
            os.chdir(self.cli_dir)
            
            # Setup virtual environment if it exists
            venv_python = os.path.join(self.cli_dir, "venv", "bin", "python")
            if os.path.exists(venv_python):
                python_cmd = venv_python
            else:
                python_cmd = "python"
            
            # Run CLI command
            cmd = [python_cmd, "fontgen.py"] + args
            print(f"Running CLI command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            os.chdir(original_dir)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            os.chdir(original_dir)
            return {
                "success": False,
                "error": "Command timed out",
                "stdout": "",
                "stderr": "Command timed out after {timeout}s"
            }
        except Exception as e:
            os.chdir(original_dir)
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }
    
    def generate_template(self, output_path: str, characters: List[str] = None) -> Dict:
        """Generate template using CLI"""
        
        # Create temporary character list if custom characters provided
        if characters:
            # For now, just use default template - CLI doesn't support custom chars yet
            # This could be enhanced later
            pass
        
        args = ["template"]
        
        # Determine format based on output extension
        if output_path.endswith('.png'):
            args.extend(["--format", "png"])
        else:
            args.extend(["--format", "svg"])
        
        # Set output path
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        args.extend(["--output", base_name])
        
        result = self._run_cli_command(args)
        
        if result["success"]:
            # Move generated file to desired location
            cli_output = f"{self.cli_dir}/{base_name}.svg"
            if os.path.exists(cli_output):
                os.rename(cli_output, output_path)
                return {"success": True, "file_path": output_path}
        
        return {"success": False, "error": result.get("error", result.get("stderr", "Unknown error"))}
    
    def generate_font_preview(self, image_path: str, font_name: str, settings: Dict = None) -> Dict:
        """Generate font preview (SVG files) using CLI
        
        This runs the CLI up to SVG generation but doesn't create the final TTF
        """
        
        # Update CLI config if settings provided
        if settings:
            self._update_cli_config(settings)
        
        # Copy image to CLI directory for processing
        cli_image_path = os.path.join(self.cli_dir, f"temp_{font_name}.png")
        import shutil
        shutil.copy2(image_path, cli_image_path)
        
        try:
            args = ["generate", cli_image_path, "--name", font_name, "--svg-only"]
            result = self._run_cli_command(args, timeout=120)
            
            if result["success"]:
                # Look for generated SVG directory
                svg_dir = os.path.join(self.cli_dir, f"temp_files/{font_name}_svg")
                if os.path.exists(svg_dir):
                    # Move SVG directory to web app temp location
                    web_svg_dir = f"temp_files/{font_name}_svg"
                    if os.path.exists(web_svg_dir):
                        shutil.rmtree(web_svg_dir)
                    shutil.move(svg_dir, web_svg_dir)
                    
                    # Read SVG files and create character map
                    character_map = self._build_character_map(web_svg_dir)
                    
                    return {
                        "success": True,
                        "svg_dir": web_svg_dir,
                        "character_map": character_map,
                        "settings": settings or {}
                    }
            
            return {
                "success": False, 
                "error": result.get("stderr", "Font preview generation failed")
            }
            
        finally:
            # Cleanup temp image
            if os.path.exists(cli_image_path):
                os.remove(cli_image_path)
    
    def generate_final_font(self, svg_dir: str, font_name: str) -> Optional[str]:
        """Generate final TTF font from SVG directory using CLI"""
        
        # Copy SVG directory to CLI temp location
        cli_svg_dir = os.path.join(self.cli_dir, f"temp_files/{font_name}_svg")
        if os.path.exists(cli_svg_dir):
            import shutil
            shutil.rmtree(cli_svg_dir)
        
        import shutil
        shutil.copytree(svg_dir, cli_svg_dir)
        
        try:
            # Create a dummy image file (CLI expects it but won't use it for final generation)
            dummy_image = os.path.join(self.cli_dir, f"temp_{font_name}_dummy.png")
            try:
                from PIL import Image
                img = Image.new('RGB', (100, 100), color='white')
                img.save(dummy_image)
            except ImportError:
                # Fallback - create a minimal PNG file
                with open(dummy_image, 'wb') as f:
                    f.write(b'')  # Empty file as placeholder
            
            args = ["generate", dummy_image, "--name", font_name, "--from-svg", cli_svg_dir]
            result = self._run_cli_command(args, timeout=180)
            
            if result["success"]:
                # Look for generated TTF
                cli_font_path = os.path.join(self.cli_dir, f"{font_name}.ttf")
                if os.path.exists(cli_font_path):
                    # Move to web app downloads
                    web_font_path = f"downloads/{font_name}.ttf"
                    shutil.move(cli_font_path, web_font_path)
                    return web_font_path
            
            return None
            
        finally:
            # Cleanup
            if os.path.exists(dummy_image):
                os.remove(dummy_image)
            if os.path.exists(cli_svg_dir):
                shutil.rmtree(cli_svg_dir)
    
    def _update_cli_config(self, settings: Dict):
        """Update CLI config.json with new settings"""
        try:
            config = self._load_config()
            
            # Update character scaling
            char_sets = config.get('font_generation', {}).get('character_sets', {})
            
            if 'uppercase_scale' in settings and 'uppercase' in char_sets:
                char_sets['uppercase']['scale_factor'] = settings['uppercase_scale']
            if 'lowercase_scale' in settings and 'lowercase' in char_sets:
                char_sets['lowercase']['scale_factor'] = settings['lowercase_scale']
            if 'numbers_scale' in settings and 'numbers' in char_sets:
                char_sets['numbers']['scale_factor'] = settings['numbers_scale']
            if 'symbols_scale' in settings and 'symbols' in char_sets:
                char_sets['symbols']['scale_factor'] = settings['symbols_scale']
            
            # Update glyph settings
            glyph_settings = config.get('font_generation', {}).get('glyph_settings', {})
            if 'space_width' in settings:
                glyph_settings['space_width'] = settings['space_width']
            if 'left_bearing' in settings:
                glyph_settings['left_bearing'] = settings['left_bearing']
            if 'right_bearing' in settings:
                glyph_settings['right_bearing'] = settings['right_bearing']
            
            # Save updated config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error updating CLI config: {e}")
    
    def _build_character_map(self, svg_dir: str) -> Dict:
        """Build character map from SVG files"""
        character_map = {}
        
        if not os.path.exists(svg_dir):
            return character_map
        
        for svg_file in os.listdir(svg_dir):
            if svg_file.endswith('.svg'):
                char_name = svg_file.replace('.svg', '')
                
                # Convert filename back to character
                actual_char = self._filename_to_char(char_name)
                
                # Read SVG content
                svg_path = os.path.join(svg_dir, svg_file)
                try:
                    with open(svg_path, 'r') as f:
                        svg_content = f.read()
                    
                    # Extract basic SVG info
                    svg_info = self._extract_svg_info(svg_content)
                    
                    character_map[actual_char] = {
                        'svg_content': svg_content,
                        'svg_info': svg_info,
                        'scale_factor': self._get_character_scale(actual_char)
                    }
                    
                except Exception as e:
                    print(f"Error reading SVG {svg_file}: {e}")
        
        return character_map
    
    def _char_to_filename(self, char: str) -> str:
        """Convert character to safe filename (matches CLI logic)"""
        char_map = {
            '/': 'slash', '\\': 'backslash', ':': 'colon',
            '*': 'asterisk', '?': 'question', '"': 'quote',
            "'": 'apostrophe', '<': 'less', '>': 'greater',
            '|': 'pipe', ' ': 'space'
        }
        
        if char in char_map:
            return char_map[char]
        elif not char.isalnum() and char not in '-_.':
            return f'char_{ord(char)}'
        else:
            return char
    
    def _filename_to_char(self, filename: str) -> str:
        """Convert safe filename back to character (matches CLI logic)"""
        char_map = {
            'slash': '/', 'backslash': '\\', 'colon': ':',
            'asterisk': '*', 'question': '?', 'quote': '"',
            'apostrophe': "'", 'less': '<', 'greater': '>',
            'pipe': '|', 'space': ' '
        }
        
        # Handle char_XXX format (ASCII codes)
        if filename.startswith('char_') and filename[5:].isdigit():
            return chr(int(filename[5:]))
        
        return char_map.get(filename, filename)
    
    def _extract_svg_info(self, svg_content: str) -> Dict:
        """Extract viewBox and path info from SVG"""
        import re
        
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        viewbox = viewbox_match.group(1) if viewbox_match else "0 0 100 100"
        
        path_matches = re.findall(r'<path[^>]*d="([^"]*)"', svg_content)
        paths = path_matches if path_matches else []
        
        return {
            'viewbox': viewbox,
            'paths': paths,
            'width': 100,
            'height': 100
        }
    
    def _get_character_scale(self, char: str) -> float:
        """Get character scale factor from config"""
        char_sets = self.config.get('font_generation', {}).get('character_sets', {})
        
        for _, char_set in char_sets.items():
            if char in char_set.get('characters', []):
                return char_set.get('scale_factor', 3.0)
        
        return 3.0  # Default scale
    
    def get_character_sets(self) -> Dict:
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