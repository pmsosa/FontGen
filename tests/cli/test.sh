#!/bin/bash

# FontGen Potrace Test Runner
# Runs comprehensive tests to verify FontForge and Potrace compatibility on M2 Mac

echo "🧪 FontGen Potrace M2 Mac Compatibility Test"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "../fontgen.py" ]; then
    echo -e "${RED}❌ Please run this script from the tests/ directory${NC}"
    exit 1
fi

# Setup virtual environment if needed (check parent directory)
if [ ! -d "../venv" ]; then
    echo -e "${YELLOW}Setting up test environment...${NC}"
    cd .. && python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd tests
else
    cd .. && source venv/bin/activate && cd tests
fi

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
echo ""

# Check FontForge
if command -v fontforge &> /dev/null; then
    echo -e "${GREEN}✅ FontForge found${NC}"
else
    echo -e "${RED}❌ FontForge not found${NC}"
    echo "Install with: brew install fontforge"
fi

# Check Potrace
if command -v potrace &> /dev/null; then
    echo -e "${GREEN}✅ Potrace found${NC}"
else
    echo -e "${RED}❌ Potrace not found${NC}"
    echo "Install with: brew install potrace"
fi

echo ""

# Run the tests
echo -e "${GREEN}Running FontGen Potrace tests...${NC}"
echo ""

python test_fontgen.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed! FontGen with Potrace is ready to use on your M2 Mac.${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    echo -e "${YELLOW}Common issues on M2 Macs:${NC}"
    echo "- FontForge not installed: brew install fontforge"
    echo "- Potrace not installed: brew install potrace"
    echo "- Missing Python dependencies: pip install -r requirements.txt"
    echo "- Config file issues (tests create their own config)"
fi