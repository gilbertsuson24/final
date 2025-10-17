#!/usr/bin/env python3
"""
Camera Diagnostic Tool for OV5647 on Raspberry Pi 5
This script helps diagnose camera connectivity and compatibility issues
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{description}")
    print("-" * 50)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Command: {' '.join(cmd)}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(cmd)}")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_system_info():
    """Check system information"""
    print("SYSTEM INFORMATION")
    print("=" * 50)
    
    # Check OS version
    run_command(['cat', '/etc/os-release'], "Operating System Version")
    
    # Check kernel version
    run_command(['uname', '-a'], "Kernel Version")
    
    # Check if running on Raspberry Pi
    run_command(['cat', '/proc/cpuinfo'], "CPU Information")

def check_camera_tools():
    """Check available camera tools"""
    print("\nCAMERA TOOLS CHECK")
    print("=" * 50)
    
    tools = [
        ('rpicam-vid', 'rpicam-apps (preferred for OV5647)'),
        ('libcamera-vid', 'libcamera-tools (fallback)'),
        ('rpicam-hello', 'rpicam test tool'),
        ('libcamera-hello', 'libcamera test tool')
    ]
    
    available_tools = []
    for tool, description in tools:
        if run_command(['which', tool], f"Checking {tool} ({description})"):
            available_tools.append(tool)
    
    return available_tools

def test_camera_detection():
    """Test camera detection with available tools"""
    print("\nCAMERA DETECTION TEST")
    print("=" * 50)
    
    # Test with rpicam if available
    if run_command(['rpicam-vid', '--list-cameras'], "Testing camera detection with rpicam-vid"):
        print("✓ Camera detected with rpicam-vid")
        return True
    
    # Test with libcamera if available
    if run_command(['libcamera-hello', '--list-cameras'], "Testing camera detection with libcamera-hello"):
        print("✓ Camera detected with libcamera-hello")
        return True
    
    print("✗ No camera detected with any tool")
    return False

def check_camera_interface():
    """Check if camera interface is enabled"""
    print("\nCAMERA INTERFACE CHECK")
    print("=" * 50)
    
    # Check if camera interface is enabled
    try:
        with open('/boot/firmware/config.txt', 'r') as f:
            config_content = f.read()
            if 'camera_auto_detect=1' in config_content or 'start_x=1' in config_content:
                print("✓ Camera interface appears to be enabled in config.txt")
            else:
                print("✗ Camera interface may not be enabled in config.txt")
                print("  Run: sudo raspi-config")
                print("  Navigate to: Interface Options > Camera > Enable")
    except FileNotFoundError:
        print("✗ Could not find /boot/firmware/config.txt")
    except Exception as e:
        print(f"Error checking config.txt: {e}")

def check_hardware_connections():
    """Check hardware connections"""
    print("\nHARDWARE CONNECTION CHECK")
    print("=" * 50)
    
    # Check if camera is detected in device tree
    run_command(['ls', '/dev/video*'], "Video devices")
    
    # Check for camera-related kernel messages
    run_command(['dmesg', '|', 'grep', '-i', 'camera'], "Camera-related kernel messages")

def provide_recommendations(available_tools, camera_detected):
    """Provide recommendations based on diagnostic results"""
    print("\nRECOMMENDATIONS")
    print("=" * 50)
    
    if not available_tools:
        print("❌ No camera tools found!")
        print("   Install camera tools:")
        print("   sudo apt update")
        print("   sudo apt install rpicam-apps libcamera-tools")
        return
    
    if 'rpicam-vid' in available_tools:
        print("✓ rpicam-vid is available (preferred for OV5647)")
    elif 'libcamera-vid' in available_tools:
        print("⚠ libcamera-vid is available (fallback option)")
    
    if not camera_detected:
        print("❌ Camera not detected!")
        print("   Possible solutions:")
        print("   1. Check camera ribbon cable connection")
        print("   2. Enable camera interface: sudo raspi-config")
        print("   3. Reboot after enabling camera interface")
        print("   4. Verify camera module is compatible")
        print("   5. Check if camera is properly seated in CSI port")
    else:
        print("✓ Camera detected successfully!")
        print("   Your camera should work with the object detection program.")

def main():
    """Main diagnostic function"""
    print("OV5647 Camera Diagnostic Tool for Raspberry Pi 5")
    print("=" * 60)
    
    # Check if running on Linux
    if sys.platform != 'linux':
        print("❌ This diagnostic tool is designed for Linux systems")
        print("   Please run this on your Raspberry Pi")
        return
    
    # Run diagnostics
    check_system_info()
    available_tools = check_camera_tools()
    camera_detected = test_camera_detection()
    check_camera_interface()
    check_hardware_connections()
    
    # Provide recommendations
    provide_recommendations(available_tools, camera_detected)
    
    print("\n" + "=" * 60)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()
