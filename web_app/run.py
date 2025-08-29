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
    # Check if running in production mode
    is_prod = os.getenv("isProd", "false").lower() == "true"
    host = "0.0.0.0" if is_prod else "127.0.0.1"
    
    print("🚀 Starting FontGen Web UI...")
    print(f"📍 Navigate to: http://localhost:8000")
    print(f"🔧 Mode: {'Production' if is_prod else 'Development'}")
    print(f"🌐 Host: {host}")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=8000,
        reload=not is_prod,  # Disable reload in production
        log_level="info"
    )