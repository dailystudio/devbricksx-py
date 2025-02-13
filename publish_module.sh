#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <module_name>"
    exit 1
fi

MODULE_NAME=$1
PROJECT_DIR=$(pwd)
SETUP_FILE="${PROJECT_DIR}/setup_${MODULE_NAME}.py"

if [ ! -f "$SETUP_FILE" ]; then
    echo "Error: setup file '$SETUP_FILE' not found!"
    exit 1
fi

echo "Cleaning old build artifacts for $MODULE_NAME..."
rm -rf dist/${MODULE_NAME}-* build/* *.egg-info

echo "Building the $MODULE_NAME package..."
python3 "$SETUP_FILE" sdist bdist_wheel

if [ ! -d "dist" ] || [ $(ls dist/${MODULE_NAME}-*.tar.gz 2>/dev/null | wc -l) -eq 0 ]; then
  echo "No build files found for $MODULE_NAME! Please check if the build process was successful."
  exit 1
fi

echo "Uploading $MODULE_NAME to PyPI..."
python3 -m twine upload dist/${MODULE_NAME}-*

echo "$MODULE_NAME release process completed!"
