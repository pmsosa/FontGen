#!/bin/bash

# FontGen Web UI Setup Script

echo "🎨 FontGen Web UI Setup"
echo "======================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the web_app directory"
    exit 1
fi

# Check dependencies
echo "🔍 Checking system dependencies..."

# Check FontForge
if ! command -v fontforge &> /dev/null; then
    echo "❌ FontForge not found!"
    echo "Install with: brew install fontforge"
    exit 1
else
    echo "✅ FontForge found"
fi

# Check Potrace
if ! command -v potrace &> /dev/null; then
    echo "❌ Potrace not found!"
    echo "Install with: brew install potrace"
    exit 1
else
    echo "✅ Potrace found"
fi

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the web UI:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "📍 Then open: http://localhost:8000"