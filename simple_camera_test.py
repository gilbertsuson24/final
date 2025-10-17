#!/usr/bin/env python3
"""
Simple Camera Test
Basic camera window test to verify OpenCV display works
"""

import cv2
import numpy as np
import time
from camera import CameraManager

def main():
    """Simple camera test"""
    print("Simple Camera Test")
    print("=" * 20)
    
    try:
        # Initialize camera
        print("Initializing camera...")
        camera = CameraManager(width=640, height=480, fps=30)
        
        if not camera.is_camera_available():
            print("Error: Camera not available")
            return False
        
        if not camera.start_camera():
            print("Error: Failed to start camera")
            return False
        
        print("Camera started successfully")
        print("Press 'q' to quit")
        
        frame_count = 0
        while True:
            # Get frame
            frame = camera.get_latest_frame()
            
            if frame is not None:
                # Add simple text overlay
                cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow("Simple Camera Test", frame)
                frame_count += 1
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            time.sleep(0.03)  # ~30 FPS
        
        # Cleanup
        cv2.destroyAllWindows()
        camera.stop_camera()
        print("Test completed")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()
