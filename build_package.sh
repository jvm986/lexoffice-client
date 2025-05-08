#!/bin/bash

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Copy stubs to the package directory
find stubs/lexoffice_client -name "*.pyi" -exec cp {} lexoffice_client/ \;

# Build the package
python setup.py sdist bdist_wheel

# Clean up - remove stubs from the package directory (optional)
# find lexoffice_client -name "*.pyi" -exec rm {} \;