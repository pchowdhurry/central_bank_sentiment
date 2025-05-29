#!/bin/bash

# Only build if the image doesn't exist
if ! docker image inspect text_analysis:latest >/dev/null 2>&1; then
  echo "🔧 Building Docker image (first time only)..."
  docker build -t text_anaysis .
else
  echo "✅ Docker image already exists. Skipping build."
fi

# Run the container
docker run -it  -v "$PWD":/app text_analysis
