from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import subprocess
import os

# Try to find poppler headers using pkg-config
def get_poppler_flags():
    try:
        # Get include directories
        include_dirs = subprocess.check_output(
            ['pkg-config', '--cflags', 'poppler-cpp'], 
            universal_newlines=True
        ).strip().replace('-I', '').split()
        
        # Get library directories and libraries
        libs = subprocess.check_output(
            ['pkg-config', '--libs', 'poppler-cpp'], 
            universal_newlines=True
        ).strip().split()
        
        # Clean up library names (remove -l prefix if present)
        clean_libs = []
        for lib in libs:
            if lib.startswith('-l'):
                clean_libs.append(lib[2:])  # Remove -l prefix
            else:
                clean_libs.append(lib)
        
        return include_dirs, clean_libs
    except:
        # Fallback to default locations
        return ['/usr/include/poppler/cpp', '/usr/include/poppler'], ['poppler-cpp']

include_dirs, libs = get_poppler_flags()

# Define the extension
extensions = [
    Extension(
        "cython_parser",
        sources=["cython_parser.pyx", "text_extract.cpp"],
        language="c++",
        include_dirs=[numpy.get_include()] + include_dirs,
        libraries=libs + ["pqxx", "pq"],
        extra_compile_args=["-std=c++17"],
        extra_link_args=["-std=c++17"]
    )
]

# Setup
setup(
    name="pdf_parser",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': 3}),
    zip_safe=False,
)