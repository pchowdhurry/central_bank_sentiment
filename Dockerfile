# Start with Ubuntu
FROM ubuntu:22.04

# Install C++ tools and Poppler library
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    make \
    gdb \ 
    pkg-config \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy everything from your computer into the container
COPY . .

# Final command: open a terminal
CMD ["bash"]