"""
FontGen Web UI - FastAPI Backend
"""

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import uuid

from core.cli_wrapper import CLIWrapper

app = FastAPI(title="FontGen Web UI", description="Generate custom TTF fonts from handwriting")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)
os.makedirs("temp_files", exist_ok=True)

# Global CLI wrapper instance  
cli_wrapper = CLIWrapper()

@app.get("/")
async def home(request: Request):
    """Main font generator page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/template-generator")
async def template_generator_page(request: Request):
    """Template generator page"""
    character_sets = cli_wrapper.get_character_sets()
    return templates.TemplateResponse("template_generator.html", {
        "request": request,
        "character_sets": character_sets
    })

@app.post("/api/generate-template")
async def generate_template(
    characters: str = Form(...),
    format: str = Form("svg"),
    filename: str = Form("font_template")
):
    """Generate template with selected characters"""
    try:
        # Parse selected characters
        selected_chars = json.loads(characters) if characters else []
        
        # Generate unique filename
        template_id = str(uuid.uuid4())[:8]
        filename = f"{filename}_{template_id}.{format}"
        output_path = f"downloads/{filename}"
        
        # Generate template using CLI
        result = cli_wrapper.generate_template(output_path, selected_chars)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate template"))
        
        return JSONResponse({
            "success": True,
            "svg_file" if format == "svg" else "png_file": filename,
            "svg_url" if format == "svg" else "png_url": f"/downloads/{filename}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Handle filled template upload"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())[:8]
        file_extension = Path(file.filename).suffix
        filename = f"template_{file_id}{file_extension}"
        file_path = f"uploads/{filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse({
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "file_path": file_path
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preview")
async def generate_preview(
    file_path: str = Form(...),
    font_name: str = Form(...),
    uppercase_scale: float = Form(4.0),
    lowercase_scale: float = Form(2.8),
    numbers_scale: float = Form(3.8),
    symbols_scale: float = Form(3.5),
    space_width: int = Form(1800),
    left_bearing: int = Form(25),
    right_bearing: int = Form(25)
):
    """Generate SVG preview without creating TTF font"""
    try:
        # Prepare settings for CLI
        settings = {
            'uppercase_scale': uppercase_scale,
            'lowercase_scale': lowercase_scale,
            'numbers_scale': numbers_scale,
            'symbols_scale': symbols_scale,
            'space_width': space_width,
            'left_bearing': left_bearing,
            'right_bearing': right_bearing
        }
        
        # Generate font preview using CLI
        result = cli_wrapper.generate_font_preview(file_path, font_name, settings)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate preview"))
        
        # Convert character map to format expected by frontend
        character_map = result["character_map"]
        svg_files = []
        
        for char, char_data in character_map.items():
            svg_files.append({
                'character': char,
                'char_name': cli_wrapper._char_to_filename(char),
                'svg_content': char_data['svg_content'],
                'svg_info': char_data['svg_info'],
                'svg_file': f"{cli_wrapper._char_to_filename(char)}.svg"
            })
        
        return JSONResponse({
            "success": True,
            "svg_dir": result["svg_dir"],
            "svg_files": svg_files,
            "character_map": character_map,
            "font_name": font_name,
            "settings": settings
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions moved to CLI wrapper

@app.post("/api/update-preview")
async def update_preview_settings(
    character_map: dict,
    uppercase_scale: float = Form(4.0),
    lowercase_scale: float = Form(2.8),
    numbers_scale: float = Form(3.8),
    symbols_scale: float = Form(3.5),
    space_width: int = Form(1800),
    left_bearing: int = Form(25),
    right_bearing: int = Form(25)
):
    """Update preview settings without regenerating SVGs"""
    try:
        # Update character scaling based on new settings
        updated_character_map = {}
        
        for char, char_data in character_map.items():
            # Determine character type and apply appropriate scaling
            scale_factor = 3.0  # Default
            
            if char.isupper():
                scale_factor = uppercase_scale
            elif char.islower():
                scale_factor = lowercase_scale
            elif char.isdigit():
                scale_factor = numbers_scale
            else:
                scale_factor = symbols_scale
            
            updated_character_map[char] = {
                **char_data,
                'scale_factor': scale_factor
            }
        
        return JSONResponse({
            "success": True,
            "character_map": updated_character_map,
            "settings": {
                'uppercase_scale': uppercase_scale,
                'lowercase_scale': lowercase_scale,
                'numbers_scale': numbers_scale,
                'symbols_scale': symbols_scale,
                'space_width': space_width,
                'left_bearing': left_bearing,
                'right_bearing': right_bearing
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-font")
async def generate_final_font(
    original_image_path: str = Form(...),
    font_name: str = Form(...)
):
    """Generate final TTF font from original image"""
    try:
        # Generate final TTF font using CLI
        font_path = cli_wrapper.generate_final_font(original_image_path, font_name)
        
        if not font_path:
            raise HTTPException(status_code=500, detail="Failed to generate font")
        
        return JSONResponse({
            "success": True,
            "font_file": f"{font_name}.ttf",
            "font_url": f"/{font_path}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return JSONResponse(cli_wrapper.config)

@app.post("/api/config")
async def update_config(settings: Dict):
    """Update configuration"""
    try:
        cli_wrapper._update_cli_config(settings)
        return JSONResponse({"success": True, "config": cli_wrapper.config})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/example-template")
async def get_example_template():
    """Serve the example template file"""
    try:
        example_file_path = Path("uploads/template_6e6e49e9.png")
        if not example_file_path.exists():
            raise HTTPException(status_code=404, detail="Example template not found")
        
        return FileResponse(
            path=str(example_file_path),
            media_type="image/png",
            filename="example-template.png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving example template: {str(e)}")

@app.get("/api/example-svgs")
async def get_example_svgs():
    """Serve the pre-generated SVG data for the example font"""
    try:
        svg_dir = Path("temp_files/MyFont_svg")
        if not svg_dir.exists():
            raise HTTPException(status_code=404, detail="Example SVG directory not found")
        
        # Load all SVG files and create character map
        character_map = {}
        
        for svg_file in svg_dir.glob("*.svg"):
            try:
                # Read SVG content
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                # Convert filename to character (e.g., "0048.svg" -> "0")
                filename = svg_file.stem  # Gets "0048" from "0048.svg"
                if filename.isdigit():
                    char = chr(int(filename))
                    character_map[char] = {
                        "svg_content": svg_content,
                        "filename": filename
                    }
                    
            except Exception as e:
                print(f"Error processing {svg_file}: {e}")
                continue
        
        return JSONResponse({
            "success": True,
            "character_map": character_map,
            "total_characters": len(character_map),
            "original_image_path": str(Path("uploads/template_6e6e49e9.png"))
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading example SVGs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)