# Start with Ubuntu
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
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

# Install Miniconda for ARM64 (aarch64)
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/conda \
    && rm miniconda.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Initialize conda for bash
RUN conda init bash

# Create text310 environment (matching your local environment)
RUN conda create -n text310 python=3.10 -y

# Install packages in text310 environment
RUN conda run -n text310 pip install cython numpy setuptools wheel pybind11

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Build the Cython extensions
RUN cd text_cleaner_cpp && conda run -n text310 python setup_cython.py build_ext --inplace
RUN cd pdf_parser_cpp && conda run -n text310 python parser_setup.py build_ext --inplace

# Set up conda environment activation in bashrc (after conda init)
RUN echo "conda activate text310" >> ~/.bashrc

# Default command - start bash with conda environment
CMD ["/bin/bash", "--login"]