#!/bin/bash

IMAGE_NAME="text_analysis"

# Check if image exists and has the required packages
check_image() {
    if docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        echo "🔍 Checking if required packages are installed..."
        docker run --rm "$IMAGE_NAME" bash -c "
            source ~/.bashrc && \
            python -c 'import cython' 2>/dev/null && \
            python -c 'import numpy' 2>/dev/null && \
            dpkg -l | grep -q libpqxx-dev && \
            dpkg -l | grep -q libpoppler-cpp-dev && \
            echo '✅ All packages found' || exit 1
        " >/dev/null 2>&1
        return $?
    else
        echo "📦 Image not found"
        return 1
    fi
}

# Build only if needed
if check_image; then
    echo "✅ Docker image is up to date"
else
    echo "🔧 Rebuilding Docker image..."
    docker build --no-cache -t "$IMAGE_NAME" .
fi

echo "🚀 Launching container..."
docker run -it --rm -v "$PWD":/app -w /app "$IMAGE_NAME" /bin/bash
