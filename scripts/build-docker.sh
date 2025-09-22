#!/bin/bash
set -e

# BPI Collector - Docker Deployment Script
# This script helps build, tag, and deploy the BPI collector Docker image

VERSION=${1:-latest}
REGISTRY=${REGISTRY:-}
PUSH=${PUSH:-false}

echo "🚀 BPI Collector Docker Deployment"
echo "=================================="
echo "Version: $VERSION"
echo "Registry: ${REGISTRY:-"local only"}"
echo "Push to registry: $PUSH"
echo

# Build function
build_image() {
    local dockerfile=$1
    local tag=$2
    
    echo "📦 Building $tag..."
    docker build -f "$dockerfile" -t "$tag" .
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully built $tag"
    else
        echo "❌ Failed to build $tag"
        exit 1
    fi
}

# Tag and push function
tag_and_push() {
    local local_tag=$1
    local remote_tag=$2
    
    if [ -n "$REGISTRY" ] && [ "$PUSH" = "true" ]; then
        echo "🏷️  Tagging $local_tag as $remote_tag"
        docker tag "$local_tag" "$remote_tag"
        
        echo "📤 Pushing $remote_tag..."
        docker push "$remote_tag"
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed $remote_tag"
        else
            echo "❌ Failed to push $remote_tag"
            exit 1
        fi
    fi
}

# Build images
echo "🔨 Building Docker images..."

# Standard image
build_image "Dockerfile" "bpi-collector:$VERSION"

# Production optimized image
build_image "Dockerfile.production" "bpi-collector:$VERSION-prod"

# Multi-architecture build (if buildx is available)
if docker buildx version >/dev/null 2>&1; then
    echo "🏗️  Building multi-architecture image..."
    docker buildx create --use --name bpi-builder 2>/dev/null || true
    
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -f Dockerfile.production \
        -t "bpi-collector:$VERSION-multiarch" \
        --load .
        
    echo "✅ Multi-architecture image built"
fi

# Tag and push to registry if specified
if [ -n "$REGISTRY" ]; then
    echo "🏷️  Tagging for registry..."
    
    tag_and_push "bpi-collector:$VERSION" "$REGISTRY/bpi-collector:$VERSION"
    tag_and_push "bpi-collector:$VERSION-prod" "$REGISTRY/bpi-collector:$VERSION-prod"
    tag_and_push "bpi-collector:$VERSION" "$REGISTRY/bpi-collector:latest"
fi

echo
echo "🎉 Docker images built successfully!"
echo
echo "Available images:"
docker images | grep bpi-collector

echo
echo "🚀 Usage Examples:"
echo "=================="
echo
echo "# Run single test:"
echo "docker run --rm -v \$(pwd)/data:/app/data bpi-collector:$VERSION --test"
echo
echo "# Run with email configuration:"
echo "docker run --rm -v \$(pwd)/data:/app/data \\"
echo "  -e SMTP_SERVER=smtp.gmail.com \\"
echo "  -e SMTP_USERNAME=user@gmail.com \\"
echo "  -e SMTP_PASSWORD=password \\"
echo "  -e EMAIL_TO=recipient@email.com \\"
echo "  bpi-collector:$VERSION --samples 60 --interval 60"
echo
echo "# Start full stack with Docker Compose:"
echo "docker compose up -d"
echo
echo "# Production optimized version:"
echo "docker run --rm bpi-collector:$VERSION-prod --test"
echo