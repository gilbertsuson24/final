#!/bin/bash
# Setup script for Raspberry Pi 5 Object Detection System
# Compatible with Debian Trixie

set -e

echo "Raspberry Pi 5 Object Detection Setup"
echo "====================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi 5"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    libcamera-tools \
    libcamera-dev \
    python3-opencv \
    libopencv-dev \
    python3-pip \
    python3-venv \
    python3-dev

# Check if camera is available
echo "Checking camera availability..."
if libcamera-hello --list-cameras >/dev/null 2>&1; then
    echo "✓ Camera detected"
else
    echo "⚠ Warning: Camera not detected. Please check camera connection."
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."

# Try tflite-runtime first (more efficient)
echo "Attempting to install tflite-runtime..."
if pip install tflite-runtime>=2.14.0; then
    echo "✓ tflite-runtime installed successfully"
else
    echo "tflite-runtime installation failed, trying full TensorFlow..."
    pip install tensorflow>=2.14.0
    echo "✓ TensorFlow installed successfully"
fi

# Install other dependencies
pip install opencv-python>=4.8.0 numpy>=1.24.0

# Create model directory if it doesn't exist
mkdir -p model

# Set up permissions
echo "Setting up permissions..."
sudo usermod -a -G video $USER

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Place your model.tflite file in the model/ directory"
echo "2. Place your labels.txt file in the model/ directory"
echo "3. Activate the virtual environment: source venv/bin/activate"
echo "4. Run the application: python3 main_controller.py"
echo ""
echo "Note: You may need to log out and back in for camera permissions to take effect."
