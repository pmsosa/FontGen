#!/bin/bash

# FontGen Test Runner
# Runs tests for CLI, webapp, or both

echo "🧪 FontGen Test Runner"
echo "====================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run CLI tests
run_cli_tests() {
    echo -e "${YELLOW}Running CLI tests...${NC}"
    cd cli
    
    if [ -f "test.sh" ]; then
        echo "📋 Running CLI integration tests..."
        ./test.sh
        cli_result=$?
    else
        echo "⚠️  No CLI test.sh found"
        cli_result=0
    fi
    
    if [ -f "test_fontgen.py" ]; then
        echo "📋 Running CLI unit tests..."
        if [ -d "../cli/venv" ]; then
            source ../cli/venv/bin/activate
        fi
        python test_fontgen.py
        cli_unit_result=$?
        cli_result=$((cli_result + cli_unit_result))
    else
        echo "⚠️  No CLI unit tests found"
    fi
    
    cd ..
    return $cli_result
}

# Function to run webapp tests
run_webapp_tests() {
    echo -e "${YELLOW}Running webapp tests...${NC}"
    cd webapp
    
    # Check if web server is running
    if curl -s http://127.0.0.1:8000 > /dev/null; then
        echo "✅ Web server is running"
        
        if [ -f "test_api.py" ]; then
            echo "📋 Running webapp API tests..."
            if [ -d "../web_app/venv" ]; then
                source ../web_app/venv/bin/activate
            fi
            python test_api.py
            api_result=$?
        else
            echo "⚠️  No webapp API tests found"
            api_result=0
        fi
        
        if [ -f "test_preview.py" ]; then
            echo "📋 Running webapp preview tests..."
            python test_preview.py
            preview_result=$?
        else
            echo "⚠️  No webapp preview tests found"
            preview_result=0
        fi
        
        webapp_result=$((api_result + preview_result))
    else
        echo "❌ Web server is not running"
        echo "   Start with: ./run_web.sh"
        webapp_result=1
    fi
    
    cd ..
    return $webapp_result
}

# Parse command line arguments
case "$1" in
    "cli")
        echo "🖥️  Running CLI tests only..."
        run_cli_tests
        exit $?
        ;;
    "webapp")
        echo "🌐 Running webapp tests only..."
        run_webapp_tests
        exit $?
        ;;
    "all"|"")
        echo "🚀 Running all tests..."
        
        echo ""
        run_cli_tests
        cli_exit_code=$?
        
        echo ""
        run_webapp_tests
        webapp_exit_code=$?
        
        # Summary
        echo ""
        echo "="*40
        echo "📊 Test Results Summary:"
        if [ $cli_exit_code -eq 0 ]; then
            echo -e "   CLI Tests: ${GREEN}✅ PASSED${NC}"
        else
            echo -e "   CLI Tests: ${RED}❌ FAILED${NC}"
        fi
        
        if [ $webapp_exit_code -eq 0 ]; then
            echo -e "   Webapp Tests: ${GREEN}✅ PASSED${NC}"
        else
            echo -e "   Webapp Tests: ${RED}❌ FAILED${NC}"
        fi
        
        total_exit_code=$((cli_exit_code + webapp_exit_code))
        
        if [ $total_exit_code -eq 0 ]; then
            echo -e "\n🎉 ${GREEN}All tests passed!${NC}"
        else
            echo -e "\n💥 ${RED}Some tests failed!${NC}"
        fi
        
        exit $total_exit_code
        ;;
    *)
        echo "Usage: $0 [cli|webapp|all]"
        echo ""
        echo "Examples:"
        echo "  $0          # Run all tests"
        echo "  $0 all      # Run all tests"
        echo "  $0 cli      # Run CLI tests only"
        echo "  $0 webapp   # Run webapp tests only"
        exit 1
        ;;
esac