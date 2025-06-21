#!/bin/bash

IMAGE_NAME="text_analysis"

echo "🔧 Rebuilding Docker image from scratch..."
docker build --no-cache -t "$IMAGE_NAME" .

echo "🚀 Launching container..."
docker run -it --rm -v "$PWD":/app -w /app "$IMAGE_NAME" bash
