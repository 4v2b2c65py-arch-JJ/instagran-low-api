#!/bin/bash
# Installation script for instagran-low-api
# Easy venv setup for Linux userland with instant deployment

set -e

echo "=== instagran-low-api Installation Script ==="
echo "Setting up virtual environment and installing dependencies..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "Installing instagran-low-api..."
pip install -e .

# Install optional dependencies for Pinecone
echo "Installing Pinecone integration..."
pip install -e ".[pinecone]"

# Create configuration directory
mkdir -p ~/.instagran-low-api
mkdir -p ~/.instagran-low-api/logs
mkdir -p ~/.instagran-low-api/cache

echo ""
echo "=== Installation Complete ==="
echo "Virtual environment: $(pwd)/venv"
echo "Configuration directory: ~/.instagran-low-api"
echo ""
echo "To activate the environment:"
echo "  source $(pwd)/venv/bin/activate"
echo ""
echo "To run the CLI:"
echo "  instagran-api --help"
echo ""
echo "To start the service:"
echo "  instagran-api serve --port 8080"
