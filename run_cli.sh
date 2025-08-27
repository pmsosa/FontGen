#!/bin/bash

# FontGen CLI - Command Line Font Generator
# Uses potrace for superior bitmap-to-vector conversion

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}FontGen CLI - Superior TTF Generation${NC}"
echo "============================================"

# Check if we're in the right directory
if [ ! -d "cli" ]; then
    echo -e "${RED}❌ Please run this script from the FontGen root directory${NC}"
    exit 1
fi

cd cli

# Check if potrace is installed
if ! command -v potrace &> /dev/null; then
    echo -e "${RED}❌ Potrace is not installed!${NC}"
    echo "Install with: brew install potrace"
    exit 1
fi

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Using potrace for superior vectorization${NC}"
echo ""

if [ $# -eq 0 ]; then
    python fontgen.py --help
else
    # Convert relative paths to absolute paths before changing directory
    args=()
    for arg in "$@"; do
        if [[ "$arg" =~ \.(png|jpg|jpeg|bmp|tiff)$ ]] && [[ ! "$arg" =~ ^/ ]]; then
            # Convert relative image path to absolute path
            abs_path="$(cd "$(dirname "../$arg")" 2>/dev/null && pwd)/$(basename "$arg")"
            if [ -f "$abs_path" ]; then
                args+=("$abs_path")
            else
                args+=("$arg")  # Keep original if conversion fails
            fi
        else
            args+=("$arg")
        fi
    done
    
    python fontgen.py "${args[@]}"
fi