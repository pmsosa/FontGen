# FontGen - Custom Font Generator

[![FontGen CI/CD Pipeline](https://github.com/pmsosa/FontGen/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/pmsosa/FontGen/actions/workflows/ci-cd.yml)

Turn your handwriting into professional TTF fonts using advanced vectorization! Available as both a **modern web UI** and **command-line interface**.

## 🚀 Quick Start

### Web UI (Recommended)
1. **Install dependencies:**
   ```bash
   # macOS
   brew install fontforge potrace
   ```

2. **Start the web interface:**
   ```bash
   ./run_web.sh
   ```

3. **Open your browser:**
   - Navigate to http://localhost:8000
   - Generate template → Draw characters → Upload → Generate font!

### Command Line
1. **Run CLI:**
   ```bash
   ./run_cli.sh template --convert-to-png
   ./run_cli.sh generate my_drawing.png --name MyCustomFont
   ```

## 🏗️ Project Structure

```
FontGen/
├── cli/                    # Command-line interface
│   ├── fontgen.py         # CLI font generator
│   ├── config.json        # Font configuration
│   └── requirements.txt   # CLI dependencies
├── web_app/               # Web interface
│   ├── main.py           # FastAPI backend
│   ├── core/             # Core font generation logic
│   ├── templates/        # HTML templates
│   └── static/           # Web assets
├── tests/                 # Test suites
│   ├── cli/              # CLI tests
│   ├── webapp/           # Web app tests
│   └── run_tests.sh      # Test runner
├── run_cli.sh            # Start CLI
└── run_web.sh            # Start web UI
```

## Requirements

- **Python 3.6+**
- **FontForge** - Font generation engine
- **Potrace** - Superior bitmap-to-vector conversion

### Installing Dependencies

**macOS:**
```bash
brew install fontforge potrace
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install fontforge potrace
```

## 🖥️ Command Line Usage

### Generate Template
```bash
./run_cli.sh template [--format svg|png] [--output filename] [--convert-to-png]
```

### Generate Font
```bash
./run_cli.sh generate <image_file> --name <font_name>
```

## 🌐 Web Interface Features

- **Real-time Preview** - See your font as you adjust settings
- **Interactive Sliders** - Live adjustment of character sizes and spacing
- **Template Generator** - Create custom character templates
- **Drag & Drop Upload** - Easy file handling
- **Character Coverage** - Visual feedback of available characters

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
./tests/run_tests.sh

# Run specific tests
./tests/run_tests.sh cli      # CLI tests only
./tests/run_tests.sh webapp   # Web app tests only
```

**Note:** Web app tests require the server to be running (`./run_web.sh`)

## Configuration

Font generation is controlled by `cli/config.json`. You can customize:

- **Character sizing** (uppercase, lowercase, numbers, symbols)
- **Spacing and metrics**
- **Vectorization settings**

### Character Sets & Scaling

The tool automatically applies different scaling for character types:
- **Uppercase letters**: Full size (4.0x scale)
- **Lowercase letters**: Smaller (3.2x scale) 
- **Numbers**: Medium (3.8x scale)
- **Symbols**: Small-medium (3.5x scale)

## Supported Characters

**94 characters total:**
- Uppercase: A-Z
- Lowercase: a-z  
- Numbers: 0-9
- Symbols: `!@#$%^&*()-_=+[]{}|;:"'<>,./?~` and more

## Advanced Features

### Potrace Vectorization
Uses potrace for superior bitmap-to-vector conversion:
- Removes template box borders automatically
- Optimized curve fitting for smooth letters
- Professional-quality vector paths

### Character-Specific Scaling
Different character types use optimized sizing:
- Maintains proper typography proportions
- Lowercase letters are appropriately smaller
- Numbers and symbols sized for readability

## Tips for Best Results

✅ **Drawing:**
- Use thick, dark strokes
- Keep characters centered in boxes
- Fill shapes completely for better vectorization
- Use high contrast (black on white)

✅ **Apps:**
- **Procreate**: Perfect for iPad drawing
- **Photoshop**: Great for precise editing
- **Any drawing app**: PNG template works everywhere

✅ **Export:**
- High resolution PNG (300+ DPI recommended)
- Maintain aspect ratio
- Dark characters on light background

## Troubleshooting

**Font appears empty in Font Book:**
- Ensure characters are dark/thick enough
- Check that drawings don't extend outside boxes
- Try increasing contrast in your drawing app

**Characters too big/small:**
- Edit `config.json` scale factors
- Regenerate font after config changes

**Spacing issues:**
- Adjust `glyph_settings` in `config.json`
- Modify `width`, `left_bearing`, `right_bearing`

## File Structure

```
FontGen/
├── fontgen.py          # Main font generator
├── start.sh           # Startup script
├── config.json        # Configuration settings
├── requirements.txt   # Python dependencies
├── temp_files/        # Processing files (auto-created)
├── tests/            # Test files
└── deleteme/         # Old/experimental files
```

## Advanced Usage

**Custom configuration:**
```bash
# Edit config.json to adjust scaling, spacing, etc.
# Then regenerate your font
./start.sh generate my_drawing.png --name UpdatedFont
```

**Batch processing:**
```bash
# Generate multiple fonts from different drawings
for drawing in *.png; do
  ./start.sh generate "$drawing" --name "${drawing%.png}Font"
done
```

---

**Created with ❤️ for custom typography**