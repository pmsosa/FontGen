# FontGen - Custom Font Generator

Create your own TTF fonts by drawing characters in templates! Uses advanced potrace vectorization for professional-quality results.

## Quick Start

1. **Install dependencies:**
   ```bash
   # macOS
   brew install fontforge potrace
   
   # Linux (Ubuntu/Debian)  
   sudo apt install fontforge potrace
   ```

2. **Generate a template:**
   ```bash
   ./start.sh template --convert-to-png
   ```

3. **Draw your characters:**
   - Import `font_template.png` into Procreate, Photoshop, or any drawing app
   - Draw your characters in each labeled box
   - Export as PNG

4. **Generate your font:**
   ```bash
   ./start.sh generate my_drawing.png --name MyCustomFont
   ```

5. **Install your font:**
   - Double-click the generated `MyCustomFont_potrace.ttf` file
   - Click "Install Font" in Font Book
   - Use your font in any app!

## Requirements

- **Python 3.6+**
- **FontForge** - Font generation engine
- **Potrace** - Superior bitmap-to-vector conversion
- **Pillow & cairosvg** - Image processing (auto-installed)

### Installing Dependencies

**macOS:**
```bash
brew install fontforge potrace
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install fontforge potrace
```

## Commands

### Generate Template
```bash
./start.sh template [--format svg|png] [--output filename] [--convert-to-png]
```

Creates a template with boxes for each character.

**Options:**
- `--format svg|png`: Template format (default: svg)
- `--output filename`: Custom filename (default: font_template)
- `--convert-to-png`: Create both SVG and high-res PNG versions

**Recommended for Procreate:**
```bash
./start.sh template --convert-to-png
```

### Generate Font
```bash
./start.sh generate <image_file> --name <font_name>
```

Converts your filled template into a professional TTF font.

**Arguments:**
- `image_file`: Path to your filled template image (PNG/JPG)
- `--name`: Name for your font (e.g., "MyHandwriting")

## Configuration

Font generation is controlled by `config.json`. You can customize:

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