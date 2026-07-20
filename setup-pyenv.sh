#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Setting up pyenv environment..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "pyenv is not installed. Please install pyenv first."
    echo "See: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# Check for .python-version file
PYTHON_VERSION_FILE=".python-version"
if [ -f "$PYTHON_VERSION_FILE" ]; then
    TARGET_VERSION=$(cat "$PYTHON_VERSION_FILE")
    echo "Found target Python version: $TARGET_VERSION"

    # Check if the target version is installed
    if ! pyenv versions --bare | grep -q "^$TARGET_VERSION$"; then
        echo "Python version $TARGET_VERSION is not installed. Installing..."
        if pyenv install "$TARGET_VERSION"; then
            echo "Successfully installed Python version $TARGET_VERSION."
        else
            echo "Failed to install Python version $TARGET_VERSION. Please check the error messages above."
            exit 1
        fi
    else
        echo "Python version $TARGET_VERSION is already installed."
    fi

    # Set the local pyenv version
    echo "Setting local Python version to $TARGET_VERSION..."
    pyenv local "$TARGET_VERSION"
    echo "Local Python version set to $(pyenv version-name)."
else
    echo "No .python-version file found in the current directory."
    echo "You may want to set a Python version using: pyenv local <version>"
fi

echo "pyenv setup script finished."
