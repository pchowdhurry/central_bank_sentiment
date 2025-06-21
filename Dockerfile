# Start with Ubuntu
FROM ubuntu:22.04

# Install C++ tools, PostgreSQL libs, and Poppler
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    make \
    git \
    pkg-config \
    libpoppler-cpp-dev \
    poppler-utils \
    libpqxx-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Default command
CMD ["bash"]
