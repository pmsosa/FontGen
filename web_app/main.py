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

from core.font_generator import FontGenerator

app = FastAPI(title="FontGen Web UI", description="Generate custom TTF fonts from handwriting")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)
os.makedirs("temp_files", exist_ok=True)

# Global font generator instance  
font_gen = FontGenerator(os.path.join("..", "config.json"))

@app.get("/")
async def home(request: Request):
    """Main font generator page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/template-generator")
async def template_generator_page(request: Request):
    """Template generator page"""
    character_sets = font_gen.get_character_sets()
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
        selected_chars = json.loads(characters) if characters else font_gen.get_all_characters()
        
        # Generate unique filename
        template_id = str(uuid.uuid4())[:8]
        svg_filename = f"{filename}_{template_id}.svg"
        svg_path = f"downloads/{svg_filename}"
        
        # Update font generator config with selected characters
        temp_config = font_gen.config.copy()
        
        # Create temporary character sets based on selection
        if isinstance(selected_chars, list):
            # Simple list of characters
            temp_config['character_sets'] = {
                'custom': {
                    'characters': selected_chars,
                    'scale_factor': 3.5,
                    'baseline_offset': 130
                }
            }
        else:
            # Character sets with categories
            temp_config['character_sets'] = selected_chars
        
        # Temporarily update generator
        original_config = font_gen.config
        font_gen.config = temp_config
        font_gen.char_properties = font_gen._build_char_properties()
        
        # Generate template
        success = font_gen.generate_template_svg(svg_path, 
            [char for char_set in temp_config['character_sets'].values() 
             for char in char_set['characters']])
        
        # Restore original config
        font_gen.config = original_config
        font_gen.char_properties = font_gen._build_char_properties()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to generate template")
        
        response_data = {
            "success": True,
            "svg_file": svg_filename,
            "svg_url": f"/downloads/{svg_filename}"
        }
        
        # Also generate PNG if requested
        if format == "png" or format == "both":
            png_filename = f"{filename}_{template_id}.png"
            png_path = f"downloads/{png_filename}"
            
            if font_gen.svg_to_png(svg_path, png_path, scale=4):
                response_data["png_file"] = png_filename
                response_data["png_url"] = f"/downloads/{png_filename}"
        
        return JSONResponse(response_data)
        
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
        # Update font generator settings
        font_gen.update_config({
            'uppercase_scale': uppercase_scale,
            'lowercase_scale': lowercase_scale,
            'numbers_scale': numbers_scale,
            'symbols_scale': symbols_scale,
            'space_width': space_width,
            'left_bearing': left_bearing,
            'right_bearing': right_bearing
        })
        
        # Generate SVG files only (fast preview)
        svg_dir = font_gen.generate_font_with_potrace(file_path, font_name)
        
        if not svg_dir:
            raise HTTPException(status_code=500, detail="Failed to generate preview")
        
        # Get list of generated SVGs
        svg_files = []
        if os.path.exists(svg_dir):
            for svg_file in os.listdir(svg_dir):
                if svg_file.endswith('.svg'):
                    char_name = svg_file.replace('.svg', '')
                    # Read SVG content
                    with open(os.path.join(svg_dir, svg_file), 'r') as f:
                        svg_content = f.read()
                    
                    svg_files.append({
                        'character': char_name,
                        'svg_content': svg_content,
                        'svg_file': svg_file
                    })
        
        return JSONResponse({
            "success": True,
            "svg_dir": svg_dir,
            "svg_files": svg_files,
            "font_name": font_name
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-font")
async def generate_final_font(
    svg_dir: str = Form(...),
    font_name: str = Form(...)
):
    """Generate final TTF font from SVGs"""
    try:
        # Generate final TTF font
        font_path = font_gen.generate_final_font(svg_dir, font_name)
        
        if not font_path:
            raise HTTPException(status_code=500, detail="Failed to generate font")
        
        # Move font to downloads directory
        download_path = f"downloads/{font_name}.ttf"
        if os.path.exists(font_path):
            shutil.move(font_path, download_path)
        
        return JSONResponse({
            "success": True,
            "font_file": f"{font_name}.ttf",
            "font_url": f"/downloads/{font_name}.ttf"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return JSONResponse(font_gen.config)

@app.post("/api/config")
async def update_config(settings: Dict):
    """Update configuration"""
    try:
        font_gen.update_config(settings)
        return JSONResponse({"success": True, "config": font_gen.config})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)