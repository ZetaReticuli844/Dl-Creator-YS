#!/bin/bash

# DL Creator Docker Hub Push Script
# This script builds and pushes all images to Docker Hub

set -e

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

# Configuration
DOCKER_USERNAME=${DOCKER_USERNAME:-"your-dockerhub-username"}
IMAGE_PREFIX=${IMAGE_PREFIX:-"dl-creator"}
VERSION=${VERSION:-"latest"}
REGISTRY=${REGISTRY:-"docker.io"}

# Function to check if Docker is logged in
check_docker_login() {
    if ! docker info | grep -q "Username"; then
        print_error "You are not logged in to Docker Hub. Please run: docker login"
        exit 1
    fi
    print_success "Docker Hub login verified"
}

# Function to build and push image
build_and_push() {
    local service_name=$1
    local context=$2
    local dockerfile=$3
    local image_name="${DOCKER_USERNAME}/${IMAGE_PREFIX}-${service_name}"
    
    print_status "Building ${service_name} image..."
    
    # Build the image
    docker build -t "${image_name}:${VERSION}" -f "${dockerfile}" "${context}"
    
    # Tag as latest
    docker tag "${image_name}:${VERSION}" "${image_name}:latest"
    
    print_status "Pushing ${service_name} image to Docker Hub..."
    
    # Push both version and latest tags
    docker push "${image_name}:${VERSION}"
    docker push "${image_name}:latest"
    
    print_success "${service_name} image pushed successfully!"
    echo "  Image: ${image_name}:${VERSION}"
    echo "  Image: ${image_name}:latest"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [SERVICES]"
    echo ""
    echo "Options:"
    echo "  -u, --username USERNAME    Docker Hub username (default: your-dockerhub-username)"
    echo "  -p, --prefix PREFIX        Image prefix (default: dl-creator)"
    echo "  -v, --version VERSION      Image version (default: latest)"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Services:"
    echo "  frontend                   Build and push frontend image"
    echo "  backend                    Build and push backend image"
    echo "  chatbot                    Build and push chatbot image"
    echo "  all                        Build and push all images (default)"
    echo ""
    echo "Examples:"
    echo "  $0 --username myuser --prefix dl-app --version v1.0.0"
    echo "  $0 frontend backend"
    echo "  $0 all"
}

# Parse command line arguments
SERVICES=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username)
            DOCKER_USERNAME="$2"
            shift 2
            ;;
        -p|--prefix)
            IMAGE_PREFIX="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        frontend|backend|chatbot|all)
            SERVICES+=("$1")
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Default to all services if none specified
if [ ${#SERVICES[@]} -eq 0 ]; then
    SERVICES=("all")
fi

# Check Docker login
check_docker_login

print_status "Starting Docker Hub push process..."
print_status "Username: ${DOCKER_USERNAME}"
print_status "Image Prefix: ${IMAGE_PREFIX}"
print_status "Version: ${VERSION}"
echo ""

# Build and push images based on selected services
for service in "${SERVICES[@]}"; do
    case $service in
        "all")
            print_status "Building and pushing all images..."
            build_and_push "frontend" "./frontend/dl-creator" "Dockerfile"
            build_and_push "backend" "./backend/dl_creator" "Dockerfile"
            build_and_push "chatbot" "./chatbot" "Dockerfile"
            ;;
        "frontend")
            build_and_push "frontend" "./frontend/dl-creator" "Dockerfile"
            ;;
        "backend")
            build_and_push "backend" "./backend/dl_creator" "Dockerfile"
            ;;
        "chatbot")
            build_and_push "chatbot" "./chatbot" "Dockerfile"
            ;;
    esac
done

print_success "All images pushed to Docker Hub successfully!"
echo ""
print_status "Image URLs:"
echo "  Frontend: ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_PREFIX}-frontend:${VERSION}"
echo "  Backend: ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_PREFIX}-backend:${VERSION}"
echo "  Chatbot: ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_PREFIX}-chatbot:${VERSION}"
echo ""
print_status "To use these images, update your docker-compose.yml with:"
echo "  image: ${DOCKER_USERNAME}/${IMAGE_PREFIX}-frontend:${VERSION}"
echo "  image: ${DOCKER_USERNAME}/${IMAGE_PREFIX}-backend:${VERSION}"
echo "  image: ${DOCKER_USERNAME}/${IMAGE_PREFIX}-chatbot:${VERSION}"
