#!/usr/bin/env python3
"""
FontGen Web UI Launcher
"""

import uvicorn
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting FontGen Web UI...")
    print("📍 Navigate to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )