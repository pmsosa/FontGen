#!/bin/bash

# FontGen Docker Build and Test Script

set -e

echo "🐳 FontGen Docker Build and Test"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Build the Docker image
print_status "Building Docker image..."
docker build -t fontgen:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Test the container
print_status "Testing container startup..."
CONTAINER_ID=$(docker run -d -p 8000:8000 --name fontgen-test fontgen:latest)

if [ $? -eq 0 ]; then
    print_success "Container started successfully"
else
    print_error "Container startup failed"
    exit 1
fi

# Wait for container to be ready
print_status "Waiting for container to be ready..."
sleep 10

# Check if container is running
if docker ps | grep -q fontgen-test; then
    print_success "Container is running"
else
    print_error "Container is not running"
    docker logs fontgen-test
    docker rm -f fontgen-test
    exit 1
fi

# Test health check
print_status "Testing health check..."
for i in {1..6}; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_success "Health check passed - Web UI is responding"
        break
    else
        if [ $i -eq 6 ]; then
            print_error "Health check failed after 6 attempts"
            docker logs fontgen-test
            docker rm -f fontgen-test
            exit 1
        fi
        print_warning "Health check attempt $i failed, retrying in 5 seconds..."
        sleep 5
    fi
done

# Test basic functionality
print_status "Testing basic functionality..."

# Test config endpoint
if curl -f http://localhost:8000/api/config > /dev/null 2>&1; then
    print_success "Config API endpoint is working"
else
    print_warning "Config API endpoint is not responding"
fi

# Test template generation
if curl -f http://localhost:8000/api/template > /dev/null 2>&1; then
    print_success "Template API endpoint is working"
else
    print_warning "Template API endpoint is not responding"
fi

# Clean up test container
print_status "Cleaning up test container..."
docker rm -f fontgen-test

print_success "Docker container test completed successfully!"
print_status "You can now run: docker-compose up -d"
print_status "Or build and run manually: docker run -p 8000:8000 fontgen:latest"

echo ""
echo "🎉 FontGen Docker container is ready for deployment!"
