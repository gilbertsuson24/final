#!/usr/bin/env python3
"""
Simple Camera Window - Non-threaded version
This version runs the camera window in the main thread
"""

import cv2
import numpy as np
import time
from camera import CameraManager

class SimpleCameraWindow:
    """Simple camera window without threading"""
    
    def __init__(self, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.camera = None
        self.is_running = False
        self.window_name = "Camera Feed - Confidence Display"
        
        # Detection data
        self.current_detection = None
        
        # Display settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.thickness = 2
    
    def start_camera(self):
        """Start camera"""
        try:
            self.camera = CameraManager(width=self.width, height=self.height, fps=self.fps)
            
            if not self.camera.is_camera_available():
                print("Error: Camera not available for camera window")
                return False
            
            if not self.camera.start_camera():
                print("Error: Failed to start camera for camera window")
                return False
            
            print("Camera window camera started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera window: {e}")
            return False
    
    def update_detection(self, class_name, confidence):
        """Update detection data"""
        self.current_detection = (class_name, confidence)
    
    def draw_confidence_overlay(self, frame):
        """Draw confidence overlay on frame"""
        display_frame = frame.copy()
        height, width = display_frame.shape[:2]
        
        # Get current detection
        if self.current_detection:
            class_name, confidence = self.current_detection
        else:
            class_name, confidence = "No detection", 0.0
        
        # Create overlay
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (10, 10), (width - 10, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
        
        # Text colors based on confidence
        if confidence > 0.7:
            text_color = (0, 255, 0)  # Green
        elif confidence > 0.5:
            text_color = (0, 255, 255)  # Yellow
        else:
            text_color = (0, 0, 255)  # Red
        
        # Draw text
        cv2.putText(display_frame, f"Object: {class_name}", (20, 35), 
                   self.font, self.font_scale, text_color, self.thickness)
        cv2.putText(display_frame, f"Confidence: {confidence:.1%}", (20, 60), 
                   self.font, self.font_scale, text_color, self.thickness)
        
        status = "DETECTED" if confidence > 0.5 else "NO DETECTION"
        cv2.putText(display_frame, f"Status: {status}", (20, 85), 
                   self.font, self.font_scale, text_color, self.thickness)
        
        # Draw confidence bar
        bar_width = 300
        bar_height = 30
        bar_x = width - bar_width - 20
        bar_y = 20
        
        # Background bar
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                      (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Confidence bar
        confidence_width = int(bar_width * confidence)
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                      (bar_x + confidence_width, bar_y + bar_height), text_color, -1)
        
        # Border
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                      (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        # Confidence percentage
        confidence_percent = f"{confidence:.1%}"
        text_size = cv2.getTextSize(confidence_percent, self.font, self.font_scale, self.thickness)[0]
        text_x = bar_x + (bar_width - text_size[0]) // 2
        text_y = bar_y + (bar_height + text_size[1]) // 2
        cv2.putText(display_frame, confidence_percent, (text_x, text_y), 
                   self.font, self.font_scale, (255, 255, 255), self.thickness)
        
        return display_frame
    
    def run(self):
        """Run the camera window"""
        if not self.start_camera():
            return False
        
        self.is_running = True
        print(f"Camera window started: {self.window_name}")
        print("Press 'q' to quit camera window, 's' to save frame")
        
        frame_count = 0
        
        while self.is_running:
            try:
                # Get frame from camera
                frame = self.camera.get_latest_frame()
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Draw confidence overlay
                display_frame = self.draw_confidence_overlay(frame)
                
                # Display frame
                cv2.imshow(self.window_name, display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.is_running = False
                elif key == ord('s'):
                    # Save current frame
                    filename = f"camera_window_{int(time.time())}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"Frame saved as {filename}")
                
                frame_count += 1
                
            except KeyboardInterrupt:
                print("\nCamera window interrupted by user")
                self.is_running = False
            except Exception as e:
                print(f"Error in camera window loop: {e}")
                time.sleep(0.1)
        
        # Cleanup
        cv2.destroyAllWindows()
        if self.camera:
            self.camera.stop_camera()
        print("Camera window stopped")
        return True

def main():
    """Test the simple camera window"""
    print("Simple Camera Window Test")
    print("=" * 30)
    
    # Create camera window
    camera_window = SimpleCameraWindow(width=640, height=480, fps=30)
    
    # Simulate some detections
    import threading
    def simulate_detections():
        import random
        classes = ["crumpled paper", "disposable cup", "plastic bottle", "No detection"]
        while camera_window.is_running:
            if random.random() > 0.3:
                class_name = random.choice(classes[:-1])
                confidence = random.uniform(0.3, 0.95)
            else:
                class_name = "No detection"
                confidence = random.uniform(0.0, 0.3)
            
            camera_window.update_detection(class_name, confidence)
            time.sleep(0.5)
    
    # Start detection simulation
    detection_thread = threading.Thread(target=simulate_detections, daemon=True)
    detection_thread.start()
    
    # Run camera window
    camera_window.run()

if __name__ == "__main__":
    main()
