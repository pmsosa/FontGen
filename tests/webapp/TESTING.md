# FontGen Web UI Testing Guide

## Current Status ✅

**Working Features:**
- ✅ Web server runs on http://localhost:8000
- ✅ Template generation (fixed config issue)
- ✅ File upload API endpoint
- ✅ Configuration loading
- ✅ FontGenerator initialization
- ✅ All dependencies installed (FontForge, Potrace)

## How to Test

### 1. Start the Web Application
```bash
cd FontGen/web_app
./startweb.sh
```

### 2. Run API Tests
```bash
# In another terminal
cd FontGen/web_app
source venv/bin/activate
python test_api.py
```

### 3. Test Template Generation
1. Go to http://localhost:8000/template-generator
2. Select characters (or use "English Basic")
3. Choose format (SVG, PNG, or Both)
4. Click "Generate Template"
5. **Should work** - downloads template files

### 4. Test File Upload (Simple)
1. Go to http://localhost:8000/test_upload.html
2. Select any image file
3. Click Upload
4. **Should work** - shows success message with file details

### 5. Test Main Font Generator
1. Go to http://localhost:8000
2. Try uploading an image (drag & drop or click browse)
3. Check browser console (F12 → Console) for errors
4. Should see upload progress and success message

## Known Issues & Fixes

### Issue 1: Template Generation ✅ FIXED
- **Problem:** 500 error on template generation
- **Cause:** Missing 'template_generation' config section
- **Fix:** Added fallback to existing config structure
- **Status:** ✅ Working

### Issue 2: File Upload UI 
- **Problem:** File selection opens browser file picker again
- **Symptoms:** File upload seems to not work in main UI
- **API Status:** ✅ Working (test_api.py passes)
- **UI Status:** 🔍 Testing needed
- **Added:** Better error handling and console logging

## Testing Checklist

**Template Generator:**
- [ ] Character selection works
- [ ] English Basic preset works
- [ ] Spanish extensions work
- [ ] SVG download works
- [ ] PNG download works

**File Upload:**
- [ ] Drag & drop works
- [ ] Click to browse works
- [ ] Upload progress shows
- [ ] Success message appears
- [ ] Generate Preview button enables

**Font Generation:**
- [ ] Preview generation works
- [ ] Real-time sliders work
- [ ] Character coverage shows
- [ ] SVG characters render
- [ ] Final TTF generation works

## Debug Commands

**Check server logs:**
```bash
# Server shows requests in terminal
tail -f server_output.log
```

**Check API directly:**
```bash
# Test template generation
curl -X POST http://localhost:8000/api/generate-template \
  -F 'characters=["A","B","C"]' \
  -F 'format=svg' \
  -F 'filename=test'

# Test file upload
curl -X POST http://localhost:8000/api/upload-image \
  -F 'file=@test_image.png'
```

**Browser console:**
1. Open browser dev tools (F12)
2. Go to Console tab
3. Look for JavaScript errors
4. File upload shows detailed logging

## Next Steps

1. **Test the main UI file upload** - check console for errors
2. **Test preview generation** - should work with uploaded files
3. **Test real-time sliders** - should update preview live
4. **Test final font generation** - creates downloadable TTF

## Files Overview

- `main.py` - FastAPI server with all endpoints
- `core/font_generator.py` - Core font generation logic
- `templates/` - HTML templates with JavaScript
- `test_api.py` - API endpoint tests
- `test_upload.html` - Simple file upload test page
- `startweb.sh` - Web app startup script