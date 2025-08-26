#!/bin/bash

# FontGen Web UI Startup Script
# Activates virtual environment and runs the web application with hot reload

echo "🚀 Starting FontGen Web UI..."
echo "============================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the web_app directory"
    echo "   cd /path/to/FontGen/web_app"
    echo "   ./startweb.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run ./setup.sh first to set up the environment"
    exit 1
fi

# Check system dependencies
echo "🔍 Checking dependencies..."

if ! command -v fontforge &> /dev/null; then
    echo "⚠️  FontForge not found - install with: brew install fontforge"
fi

if ! command -v potrace &> /dev/null; then
    echo "⚠️  Potrace not found - install with: brew install potrace"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if FastAPI is installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Start the web application
echo ""
echo "🌟 Starting FontGen Web UI with hot reload..."
echo "📍 Navigate to: http://localhost:8000"
echo "🔄 Hot reload enabled - changes will auto-refresh"
echo "🛑 Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the web application with hot reload
python run.py