#!/usr/bin/env python3
"""
Test Camera Window - Diagnostic Version
This script tests the camera window functionality step by step
"""

import cv2
import numpy as np
import time
import sys
from camera_window import CameraWindow

def test_opencv_display():
    """Test if OpenCV can display windows"""
    print("Testing OpenCV display capability...")
    
    try:
        # Create a simple test window
        test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.putText(test_image, "OpenCV Test Window", (50, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        print("Displaying test window for 3 seconds...")
        cv2.imshow("OpenCV Test", test_image)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()
        print("✓ OpenCV display test passed")
        return True
    except Exception as e:
        print(f"✗ OpenCV display test failed: {e}")
        return False

def test_camera_window_simple():
    """Test camera window with simple setup"""
    print("\nTesting camera window...")
    
    try:
        # Create camera window
        camera_window = CameraWindow(width=640, height=480, fps=30)
        
        # Test if camera is available
        if not camera_window.camera.is_camera_available():
            print("✗ Camera not available for camera window")
            return False
        
        # Start camera
        if not camera_window.camera.start_camera():
            print("✗ Failed to start camera for camera window")
            return False
        
        print("✓ Camera started for camera window")
        
        # Test frame capture
        print("Testing frame capture...")
        for i in range(5):
            frame = camera_window.camera.get_latest_frame()
            if frame is not None:
                print(f"✓ Frame {i+1} captured successfully")
                break
            time.sleep(0.5)
        else:
            print("✗ No frames captured")
            return False
        
        # Test window display
        print("Testing window display...")
        camera_window.update_detection("Test Object", 0.85)
        display_frame = camera_window.draw_confidence_overlay(frame)
        
        print("Displaying camera window for 5 seconds...")
        print("Look for a window titled 'Camera Feed - Confidence Display'")
        cv2.imshow("Camera Feed - Confidence Display", display_frame)
        
        # Wait for key press or timeout
        start_time = time.time()
        while time.time() - start_time < 5:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            time.sleep(0.1)
        
        cv2.destroyAllWindows()
        camera_window.camera.stop_camera()
        print("✓ Camera window test completed")
        return True
        
    except Exception as e:
        print(f"✗ Camera window test failed: {e}")
        return False

def test_environment():
    """Test environment variables and display"""
    print("Testing environment...")
    
    # Check if running in headless mode
    display = os.environ.get('DISPLAY')
    if not display:
        print("⚠ No DISPLAY environment variable found")
        print("  This might cause issues with OpenCV windows")
    else:
        print(f"✓ DISPLAY set to: {display}")
    
    # Check if running over SSH
    ssh_client = os.environ.get('SSH_CLIENT')
    if ssh_client:
        print("⚠ Running over SSH - OpenCV windows may not display")
        print("  Try running directly on the Raspberry Pi")
    else:
        print("✓ Not running over SSH")

def main():
    """Main test function"""
    print("Camera Window Diagnostic Test")
    print("=" * 40)
    
    # Test environment
    test_environment()
    
    # Test OpenCV display
    if not test_opencv_display():
        print("\n❌ OpenCV display test failed!")
        print("Possible solutions:")
        print("1. Make sure you're running directly on the Raspberry Pi (not over SSH)")
        print("2. Check if you have a display connected")
        print("3. Try running: export DISPLAY=:0")
        return False
    
    # Test camera window
    if not test_camera_window_simple():
        print("\n❌ Camera window test failed!")
        print("Possible solutions:")
        print("1. Check camera connection")
        print("2. Run: python3 camera_diagnostic.py")
        print("3. Check if camera is being used by another process")
        return False
    
    print("\n✅ All tests passed!")
    print("The camera window should work with the main controller.")
    return True

if __name__ == "__main__":
    import os
    main()
