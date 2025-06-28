from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Define the extension
extensions = [
    Extension(
        "speech_clean_wrapper",
        sources=["speech_clean_wrapper.pyx", "speech_clean.cpp"],
        language="c++",
        extra_compile_args=[
            "-std=c++11",
            "-O3",
            "-Wall",
            "-Wextra"
        ],
        extra_link_args=[
            "-std=c++11"
        ],
        libraries=["pqxx", "pq"],  # PostgreSQL libraries
        include_dirs=[np.get_include()],  # NumPy headers if needed
    )
]

# Setup configuration
setup(
    name="speech_clean_wrapper",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': 3,
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
        'nonecheck': False,
    }),
    zip_safe=False,
    install_requires=[
        'cython>=3.0.0',
        'numpy',
    ],
) 