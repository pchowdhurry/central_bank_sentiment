#!/bin/bash

# Build script for Cython wrapper
echo "Building Cython wrapper for Clean_Text..."

# Check if we're in the right directory
if [ ! -f "speech_clean.hpp" ]; then
    echo "Error: speech_clean.hpp not found. Please run this script from the text_cleaner_cpp directory."
    exit 1
fi

# Determine Python command
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Neither 'python3' nor 'python' command found."
    echo "Please ensure Python is installed and accessible."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Install dependencies if needed
echo "Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements_cython.txt

# Build the extension
echo "Building Cython extension..."
$PYTHON_CMD setup_cython.py build_ext --inplace

if [ $? -eq 0 ]; then
    echo "Build successful! You can now import speech_clean_wrapper in Python."
    echo "Test it with: $PYTHON_CMD test_cython.py"
else
    echo "Build failed. Please check the error messages above."
    exit 1
fi 