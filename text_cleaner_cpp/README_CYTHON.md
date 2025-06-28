# Cython Wrapper for Clean_Text

This directory contains a Cython wrapper for the `Clean_Text` C++ class, providing a Python interface for text cleaning functionality.

## Files Overview

- `speech_clean_wrapper.pyx` - Cython wrapper file
- `setup_cython.py` - Build configuration for the Cython extension
- `test_cython.py` - Test script to verify the wrapper works
- `integration_example.py` - Example showing integration with Python scrapers
- `build_cython.sh` - Build script to compile the extension
- `requirements_cython.txt` - Python dependencies

## Prerequisites

1. **Cython**: `pip install cython>=3.0.0`
2. **C++ Compiler**: GCC or Clang with C++11 support
3. **PostgreSQL Libraries**: For database functionality (libpqxx, libpq)

### Installing PostgreSQL Libraries (macOS)
```bash
# Using Homebrew
brew install postgresql libpqxx

# Or using MacPorts
sudo port install postgresql11 libpqxx
```

## Building the Extension

1. Navigate to the `text_cleaner_cpp` directory:
```bash
cd text_cleaner_cpp
```

2. Run the build script:
```bash
./build_cython.sh
```

This will:
- Install required Python dependencies
- Compile the Cython extension
- Create `speech_clean_wrapper.so` (or `.pyd` on Windows)

## Usage

### Basic Usage

```python
from speech_clean_wrapper import PyCleanText

# Create a cleaner instance
cleaner = PyCleanText(
    raw_text="Your text to clean here...",
    file_name="output.txt",
    min_chars=10
)

# Process the text
cleaner.process_text()

# Get results
sentence_count = cleaner.get_sentence_count()
sentences = cleaner.get_sentences()

# Save to file
cleaner.write_to_file()

# Save to database (optional)
cleaner.add_to_db(
    db_name="your_db",
    user="your_user",
    password="your_password",
    host="localhost",
    port=5432,
    table_name="speeches"
)
```

### Integration with Scrapers

```python
# Example integration with your existing scrapers
from speech_clean_wrapper import PyCleanText

def process_scraped_speech(speech_text, output_file):
    cleaner = PyCleanText(
        raw_text=speech_text,
        file_name=output_file,
        min_chars=15
    )
    
    cleaner.process_text()
    cleaner.write_to_file()
    
    return cleaner.get_sentences()
```

## Testing

Run the test script to verify everything works:

```bash
python test_cython.py
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've built the extension first
   ```bash
   cd text_cleaner_cpp && ./build_cython.sh
   ```

2. **PostgreSQL Libraries Not Found**: Install the required libraries
   ```bash
   # macOS
   brew install postgresql libpqxx
   
   # Ubuntu/Debian
   sudo apt-get install libpq-dev libpqxx-dev
   ```

3. **C++ Compiler Issues**: Ensure you have a C++11 compatible compiler
   ```bash
   # Check GCC version
   gcc --version
   
   # Should be 4.8+ for C++11 support
   ```

4. **Permission Errors**: Make the build script executable
   ```bash
   chmod +x build_cython.sh
   ```

### Manual Build

If the build script fails, you can build manually:

```bash
# Install dependencies
pip install -r requirements_cython.txt

# Build extension
python setup_cython.py build_ext --inplace
```

## Advantages of Cython over pybind11

1. **Better Error Messages**: Cython provides clearer error messages during compilation
2. **More Mature**: Cython has been around longer and is more stable
3. **Easier Debugging**: Better integration with Python debugging tools
4. **No Header Issues**: Avoids the pybind11 header compatibility problems you encountered
5. **Better Performance**: Can be faster than pybind11 in many cases

## Performance Notes

- The Cython wrapper provides near-native C++ performance
- String encoding/decoding overhead is minimal
- Memory management is handled automatically
- The wrapper is thread-safe for read operations

## Next Steps

1. Build the extension using `./build_cython.sh`
2. Test with `python test_cython.py`
3. Integrate with your existing scrapers using the examples in `integration_example.py`
4. Customize the wrapper as needed for your specific use case 