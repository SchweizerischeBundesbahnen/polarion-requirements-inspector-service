#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Dockerfile tests...${NC}"

# Function to clean up containers and images
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    docker stop requirements_inspector_service 2>/dev/null || true
    docker rm requirements_inspector_service 2>/dev/null || true
    docker rmi requirements_inspector_service 2>/dev/null || true
}

# Ensure cleanup runs even if script fails
trap cleanup EXIT

# Test 1: Check if Dockerfile exists
echo -e "\n${YELLOW}Test 1: Checking if Dockerfile exists...${NC}"
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dockerfile exists${NC}"

# Test 2: Lint Dockerfile with hadolint
echo -e "\n${YELLOW}Test 2: Linting Dockerfile with hadolint...${NC}"
if ! command -v hadolint &> /dev/null; then
    echo -e "${YELLOW}⚠️  hadolint not found, installing...${NC}"
    if [[ "$(uname)" == "Darwin" ]]; then
        brew install hadolint
    else
        curl -L -o /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
        chmod +x /usr/local/bin/hadolint
    fi
fi
if hadolint Dockerfile; then
    echo -e "${GREEN}✓ Dockerfile passed linting${NC}"
else
    echo -e "${RED}❌ Dockerfile failed linting${NC}"
    exit 1
fi

# Test 3: Build Docker image
echo -e "\n${YELLOW}Test 3: Building Docker image...${NC}"
if docker build -t requirements_inspector_service --build-arg APP_IMAGE_VERSION=3.0.0 .; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker image build failed${NC}"
    exit 1
fi

# Test 4: Run container tests
echo -e "\n${YELLOW}Test 4: Running container tests...${NC}"
if uv run pytest tests/test_container.py -v; then
    echo -e "${GREEN}✓ Container tests passed${NC}"
else
    echo -e "${RED}❌ Container tests failed${NC}"
    exit 1
fi

# Test 5: Check image size
echo -e "\n${YELLOW}Test 5: Checking image size...${NC}"
IMAGE_SIZE=$(docker image inspect requirements_inspector_service --format='{{.Size}}')
MAX_SIZE=$((1024 * 1024 * 1024)) # 1GB
if [ "$IMAGE_SIZE" -gt "$MAX_SIZE" ]; then
    echo -e "${RED}❌ Image size ($(numfmt --to=iec-i --suffix=B $IMAGE_SIZE)) exceeds 1GB${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Image size ($(numfmt --to=iec-i --suffix=B $IMAGE_SIZE)) is within limits${NC}"

# Test 6: Check if container runs and is healthy
echo -e "\n${YELLOW}Test 6: Testing container health...${NC}"
docker run -d --name requirements_inspector_service -p 9081:9081 requirements_inspector_service
sleep 5

if curl -f http://localhost:9081/version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Container is healthy and responding${NC}"
else
    echo -e "${RED}❌ Container is not responding${NC}"
    exit 1
fi

echo -e "\n${GREEN}All tests passed successfully! 🎉${NC}"
