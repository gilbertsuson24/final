"""
Camera Window for displaying camera feed with confidence levels
"""

import cv2
import numpy as np
import threading
import time
from typing import Optional, Tuple, Callable
from camera import CameraManager


class CameraWindow:
    """Separate camera window with confidence display"""
    
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        """
        Initialize camera window
        
        Args:
            width: Camera resolution width
            height: Camera resolution height
            fps: Frames per second
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.camera = None
        self.is_running = False
        self.window_name = "Camera Feed - Confidence Display"
        
        # Detection data
        self.current_detection = None
        self.detection_lock = threading.Lock()
        
        # Display settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.thickness = 2
        
    def start_camera(self) -> bool:
        """
        Start camera for the window
        
        Returns:
            bool: True if camera started successfully
        """
        try:
            self.camera = CameraManager(width=self.width, height=self.height, fps=self.fps)
            
            if not self.camera.is_camera_available():
                print("Error: Camera not available for window")
                return False
            
            if not self.camera.start_camera():
                print("Error: Failed to start camera for window")
                return False
            
            print("Camera window camera started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera window: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera and cleanup"""
        self.is_running = False
        if self.camera:
            self.camera.stop_camera()
        cv2.destroyAllWindows()
        print("Camera window stopped")
    
    def update_detection(self, class_name: str, confidence: float):
        """
        Update the current detection data
        
        Args:
            class_name: Detected class name
            confidence: Detection confidence (0.0 to 1.0)
        """
        with self.detection_lock:
            self.current_detection = (class_name, confidence)
    
    def draw_confidence_overlay(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw confidence information on the frame
        
        Args:
            frame: Input frame
            
        Returns:
            np.ndarray: Frame with confidence overlay
        """
        display_frame = frame.copy()
        height, width = display_frame.shape[:2]
        
        # Get current detection
        with self.detection_lock:
            if self.current_detection:
                class_name, confidence = self.current_detection
            else:
                class_name, confidence = "No detection", 0.0
        
        # Create semi-transparent overlay
        overlay = display_frame.copy()
        
        # Draw background for text area
        text_area_height = 120
        cv2.rectangle(overlay, (10, 10), (width - 10, text_area_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
        
        # Draw detection information
        detection_text = f"Object: {class_name}"
        confidence_text = f"Confidence: {confidence:.1%}"
        status_text = "Status: DETECTED" if confidence > 0.5 else "Status: NO DETECTION"
        
        # Text colors based on confidence
        if confidence > 0.7:
            text_color = (0, 255, 0)  # Green for high confidence
        elif confidence > 0.5:
            text_color = (0, 255, 255)  # Yellow for medium confidence
        else:
            text_color = (0, 0, 255)  # Red for low/no confidence
        
        # Draw text
        cv2.putText(display_frame, detection_text, (20, 35), 
                   self.font, self.font_scale, text_color, self.thickness)
        cv2.putText(display_frame, confidence_text, (20, 60), 
                   self.font, self.font_scale, text_color, self.thickness)
        cv2.putText(display_frame, status_text, (20, 85), 
                   self.font, self.font_scale, text_color, self.thickness)
        
        # Draw confidence bar
        self.draw_confidence_bar(display_frame, confidence, width, height)
        
        # Draw frame info
        self.draw_frame_info(display_frame, width, height)
        
        return display_frame
    
    def draw_confidence_bar(self, frame: np.ndarray, confidence: float, width: int, height: int):
        """
        Draw confidence bar on the frame
        
        Args:
            frame: Frame to draw on
            confidence: Confidence value (0.0 to 1.0)
            width: Frame width
            height: Frame height
        """
        # Bar dimensions
        bar_width = 300
        bar_height = 30
        bar_x = width - bar_width - 20
        bar_y = 20
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), 
                      (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Confidence bar
        confidence_width = int(bar_width * confidence)
        if confidence > 0.7:
            bar_color = (0, 255, 0)  # Green
        elif confidence > 0.5:
            bar_color = (0, 255, 255)  # Yellow
        else:
            bar_color = (0, 0, 255)  # Red
        
        cv2.rectangle(frame, (bar_x, bar_y), 
                      (bar_x + confidence_width, bar_y + bar_height), bar_color, -1)
        
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), 
                      (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        # Confidence percentage text
        confidence_percent = f"{confidence:.1%}"
        text_size = cv2.getTextSize(confidence_percent, self.font, self.font_scale, self.thickness)[0]
        text_x = bar_x + (bar_width - text_size[0]) // 2
        text_y = bar_y + (bar_height + text_size[1]) // 2
        cv2.putText(frame, confidence_percent, (text_x, text_y), 
                   self.font, self.font_scale, (255, 255, 255), self.thickness)
    
    def draw_frame_info(self, frame: np.ndarray, width: int, height: int):
        """
        Draw frame information
        
        Args:
            frame: Frame to draw on
            width: Frame width
            height: Frame height
        """
        # Frame info text
        fps_text = f"FPS: {self.fps}"
        resolution_text = f"Resolution: {width}x{height}"
        
        # Position at bottom right
        info_y = height - 20
        cv2.putText(frame, fps_text, (width - 150, info_y), 
                   self.font, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, resolution_text, (width - 150, info_y - 20), 
                   self.font, 0.5, (255, 255, 255), 1)
    
    def run_window(self):
        """Run the camera window display loop"""
        if not self.start_camera():
            return False
        
        self.is_running = True
        print(f"Camera window started: {self.window_name}")
        print("Press 'q' to quit camera window, 's' to save frame")
        
        frame_count = 0
        last_fps_time = time.time()
        fps_counter = 0
        
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
                
                # Calculate FPS
                frame_count += 1
                fps_counter += 1
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    actual_fps = fps_counter / (current_time - last_fps_time)
                    print(f"Camera window FPS: {actual_fps:.1f}")
                    fps_counter = 0
                    last_fps_time = current_time
                
            except KeyboardInterrupt:
                print("\nCamera window interrupted by user")
                self.is_running = False
            except Exception as e:
                print(f"Error in camera window loop: {e}")
                time.sleep(0.1)
        
        # Cleanup
        self.stop_camera()
        print("Camera window stopped")
        return True
    
    def run_window_threaded(self) -> threading.Thread:
        """
        Run camera window in a separate thread
        
        Returns:
            threading.Thread: Thread running the camera window
        """
        def window_thread():
            self.run_window()
        
        thread = threading.Thread(target=window_thread, daemon=True)
        thread.start()
        return thread
    
    def is_window_running(self) -> bool:
        """
        Check if window is currently running
        
        Returns:
            bool: True if window is running
        """
        return self.is_running
    
    def get_current_detection(self) -> Optional[Tuple[str, float]]:
        """
        Get current detection data
        
        Returns:
            Optional[Tuple[str, float]]: (class_name, confidence) or None
        """
        with self.detection_lock:
            return self.current_detection.copy() if self.current_detection else None
