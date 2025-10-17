#!/bin/bash
# Setup script for OV5647 camera on Raspberry Pi 5
# This script installs the necessary camera tools and dependencies

echo "Setting up OV5647 camera for Raspberry Pi 5"
echo "============================================="

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install rpicam-apps (preferred for OV5647 on Pi 5)
echo "Installing rpicam-apps..."
sudo apt install -y rpicam-apps

# Install libcamera-tools as fallback
echo "Installing libcamera-tools (fallback)..."
sudo apt install -y libcamera-tools

# Install OpenCV for Python
echo "Installing OpenCV..."
sudo apt install -y python3-opencv

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Enable camera interface
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Test camera detection
echo "Testing camera detection..."
echo "Checking for rpicam..."
if command -v rpicam-vid &> /dev/null; then
    echo "✓ rpicam-vid found"
    rpicam-vid --list-cameras
else
    echo "✗ rpicam-vid not found"
fi

echo "Checking for libcamera..."
if command -v libcamera-vid &> /dev/null; then
    echo "✓ libcamera-vid found"
    libcamera-hello --list-cameras
else
    echo "✗ libcamera-vid not found"
fi

echo ""
echo "Setup complete!"
echo "Please reboot your Raspberry Pi to ensure camera interface is properly enabled."
echo "After reboot, test the camera with: python3 main_controller.py"
