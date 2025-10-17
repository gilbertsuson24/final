#!/usr/bin/env python3
"""
Installation script for Raspberry Pi 5 Object Detection dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def install_dependencies():
    """Install all required dependencies"""
    print("Installing Raspberry Pi 5 Object Detection dependencies...")
    print("=" * 60)
    
    # Update package list
    if not run_command("sudo apt update", "Updating package list"):
        return False
    
    # Install system dependencies
    system_deps = [
        "python3-pip",
        "python3-opencv",
        "libcamera-dev",
        "rpicam-apps"
    ]
    
    for dep in system_deps:
        if not run_command(f"sudo apt install -y {dep}", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep}")
    
    # Install Python dependencies
    print("\nInstalling Python dependencies...")
    
    # Try tflite-runtime first
    print("Attempting to install tflite-runtime...")
    if run_command("pip3 install tflite-runtime>=2.14.0", "Installing tflite-runtime"):
        print("✓ tflite-runtime installed successfully")
    else:
        print("tflite-runtime installation failed, trying full TensorFlow...")
        if not run_command("pip3 install tensorflow>=2.14.0", "Installing TensorFlow"):
            print("✗ Failed to install TensorFlow")
            return False
        print("✓ TensorFlow installed successfully")
    
    # Install other Python dependencies
    other_deps = [
        "opencv-python>=4.8.0",
        "numpy>=1.24.0"
    ]
    
    for dep in other_deps:
        if not run_command(f"pip3 install {dep}", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep}")
    
    print("\n" + "=" * 60)
    print("Installation completed!")
    print("\nTo test the installation, run:")
    print("  python3 test_imports.py")
    print("\nTo run the object detection system:")
    print("  python3 main_controller.py")
    
    return True

if __name__ == "__main__":
    success = install_dependencies()
    if not success:
        print("\nInstallation failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\nInstallation successful!")
