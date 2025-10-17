#!/usr/bin/env python3
"""
Main Controller for Raspberry Pi 5 Object Detection
Uses OV5647 camera with rpicam and TensorFlow Lite for object detection
"""

import cv2
import numpy as np
import time
import os
import sys
from typing import Tuple, Optional

# Import our custom modules
from camera import CameraManager
from model import ModelLoader
from camera_window import CameraWindow


class ObjectDetectionController:
    """Main controller for object detection application"""
    
    def __init__(self, model_path: str = "model/model.tflite", 
                 labels_path: str = "model/labels.txt"):
        """
        Initialize the object detection controller
        
        Args:
            model_path: Path to TensorFlow Lite model
            labels_path: Path to labels file
        """
        self.model_path = model_path
        self.labels_path = labels_path
        self.camera = None
        self.model = None
        self.is_running = False
        self.camera_window = None
        self.show_camera_window = False
        
        # Detection parameters
        self.confidence_threshold = 0.5
        self.detection_history = []
        self.max_history = 10
        
    def initialize_camera(self) -> bool:
        """
        Initialize camera system
        
        Returns:
            bool: True if camera initialized successfully
        """
        try:
            self.camera = CameraManager(width=640, height=480, fps=30)
            
            # Check if camera is available
            if not self.camera.is_camera_available():
                print("Error: Camera not available. Please check camera connection.")
                print("\nTroubleshooting steps:")
                print("1. Run: python3 camera_diagnostic.py")
                print("2. Check camera ribbon cable connection")
                print("3. Enable camera interface: sudo raspi-config")
                print("4. Install camera tools: sudo apt install rpicam-apps")
                print("5. Reboot after making changes")
                return False
            
            # Start camera
            if not self.camera.start_camera():
                print("Error: Failed to start camera")
                print("This may be due to:")
                print("- Camera already in use by another process")
                print("- Insufficient permissions")
                print("- Hardware connection issues")
                return False
            
            print("Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def initialize_model(self) -> bool:
        """
        Initialize TensorFlow Lite model
        
        Returns:
            bool: True if model initialized successfully
        """
        try:
            self.model = ModelLoader(self.model_path, self.labels_path)
            
            if not self.model.load_model():
                print("Error: Failed to load model")
                return False
            
            print("Model initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing model: {e}")
            return False
    
    def initialize_camera_window(self) -> bool:
        """
        Initialize camera window for separate display
        
        Returns:
            bool: True if camera window initialized successfully
        """
        try:
            self.camera_window = CameraWindow(width=640, height=480, fps=30)
            print("Camera window initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing camera window: {e}")
            return False
    
    def start_camera_window(self) -> bool:
        """
        Start camera window in separate thread
        
        Returns:
            bool: True if camera window started successfully
        """
        try:
            if not self.camera_window:
                if not self.initialize_camera_window():
                    return False
            
            # Start camera window in separate thread
            self.camera_window.run_window_threaded()
            self.show_camera_window = True
            print("Camera window started in separate thread")
            return True
        except Exception as e:
            print(f"Error starting camera window: {e}")
            return False
    
    def stop_camera_window(self):
        """Stop camera window"""
        if self.camera_window:
            self.camera_window.stop_camera()
            self.show_camera_window = False
            print("Camera window stopped")
    
    def draw_detection_info(self, frame: np.ndarray, 
                          class_name: str, confidence: float) -> np.ndarray:
        """
        Draw detection information on frame
        
        Args:
            frame: Input frame
            class_name: Detected class name
            confidence: Detection confidence
            
        Returns:
            np.ndarray: Frame with detection info drawn
        """
        # Create a copy to avoid modifying original
        display_frame = frame.copy()
        
        # Get frame dimensions
        height, width = display_frame.shape[:2]
        
        # Create overlay for detection info
        overlay = display_frame.copy()
        
        # Draw background rectangle for text
        cv2.rectangle(overlay, (10, 10), (width - 10, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
        
        # Draw detection text
        detection_text = f"Object: {class_name}"
        confidence_text = f"Confidence: {confidence:.1%}"
        
        # Set text properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        # Get text sizes
        (text_width, text_height), _ = cv2.getTextSize(detection_text, font, font_scale, thickness)
        
        # Draw detection text
        cv2.putText(display_frame, detection_text, (20, 40), 
                   font, font_scale, (0, 255, 0), thickness)
        
        # Draw confidence text
        cv2.putText(display_frame, confidence_text, (20, 65), 
                   font, font_scale, (0, 255, 0), thickness)
        
        # Draw confidence bar
        bar_width = 200
        bar_height = 20
        bar_x = width - bar_width - 20
        bar_y = 20
        
        # Background bar
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Confidence bar
        confidence_width = int(bar_width * confidence)
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                     (bar_x + confidence_width, bar_y + bar_height), (0, 255, 0), -1)
        
        # Draw border
        cv2.rectangle(display_frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        return display_frame
    
    def update_detection_history(self, class_name: str, confidence: float):
        """
        Update detection history for smoothing
        
        Args:
            class_name: Detected class name
            confidence: Detection confidence
        """
        self.detection_history.append((class_name, confidence, time.time()))
        
        # Keep only recent detections
        if len(self.detection_history) > self.max_history:
            self.detection_history.pop(0)
    
    def get_smoothed_detection(self) -> Tuple[str, float]:
        """
        Get smoothed detection result from history
        
        Returns:
            Tuple[str, float]: (class_name, confidence)
        """
        if not self.detection_history:
            return "No detection", 0.0
        
        # Get recent detections (last 2 seconds)
        current_time = time.time()
        recent_detections = [
            (name, conf) for name, conf, timestamp in self.detection_history
            if current_time - timestamp < 2.0
        ]
        
        if not recent_detections:
            return "No detection", 0.0
        
        # Find most common class
        class_counts = {}
        for name, conf in recent_detections:
            class_counts[name] = class_counts.get(name, 0) + 1
        
        most_common_class = max(class_counts, key=class_counts.get)
        
        # Get average confidence for most common class
        class_confidences = [conf for name, conf in recent_detections if name == most_common_class]
        avg_confidence = sum(class_confidences) / len(class_confidences)
        
        return most_common_class, avg_confidence
    
    def run_detection_loop(self):
        """Main detection loop"""
        print("Starting object detection...")
        print("Press 'q' to quit, 's' to save current frame")
        
        self.is_running = True
        frame_count = 0
        last_detection_time = 0
        detection_interval = 0.5  # Run detection every 0.5 seconds
        
        while self.is_running:
            try:
                # Get frame from camera
                frame = self.camera.get_latest_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                current_time = time.time()
                
                # Run detection at specified interval
                if current_time - last_detection_time >= detection_interval:
                    if self.model and self.model.is_loaded():
                        # Run inference
                        class_name, confidence = self.model.predict(frame)
                        
                        # Update history
                        self.update_detection_history(class_name, confidence)
                        
                        # Update camera window if active
                        if self.camera_window and self.show_camera_window:
                            self.camera_window.update_detection(class_name, confidence)
                        
                        last_detection_time = current_time
                
                # Get smoothed detection result
                display_class, display_confidence = self.get_smoothed_detection()
                
                # Only show detections above threshold
                if display_confidence >= self.confidence_threshold:
                    frame = self.draw_detection_info(frame, display_class, display_confidence)
                else:
                    # Show "No detection" message
                    frame = self.draw_detection_info(frame, "No detection", 0.0)
                
                # Display frame
                cv2.imshow("Raspberry Pi 5 Object Detection", frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.is_running = False
                elif key == ord('s'):
                    # Save current frame
                    filename = f"detection_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Frame saved as {filename}")
                
                frame_count += 1
                
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                self.is_running = False
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(0.1)
        
        # Cleanup
        cv2.destroyAllWindows()
        if self.camera:
            self.camera.stop_camera()
        if self.camera_window:
            self.camera_window.stop_camera()
        
        print("Object detection stopped")
    
    def run(self):
        """Run the complete object detection application"""
        print("Raspberry Pi 5 Object Detection System")
        print("=" * 40)
        
        # Check if model files exist
        if not os.path.exists(self.model_path):
            print(f"Error: Model file not found: {self.model_path}")
            print("Please place your .tflite model file in the model/ directory")
            return False
        
        if not os.path.exists(self.labels_path):
            print(f"Error: Labels file not found: {self.labels_path}")
            print("Please place your labels.txt file in the model/ directory")
            return False
        
        # Initialize camera
        print("Initializing camera...")
        if not self.initialize_camera():
            return False
        
        # Initialize model
        print("Initializing model...")
        if not self.initialize_model():
            return False
        
        # Run detection loop
        try:
            self.run_detection_loop()
        except Exception as e:
            print(f"Error running detection: {e}")
            return False
        
        return True
    
    def run_with_camera_window(self):
        """Run object detection with separate camera window"""
        print("Raspberry Pi 5 Object Detection System with Camera Window")
        print("=" * 60)
        
        # Check if model files exist
        if not os.path.exists(self.model_path):
            print(f"Error: Model file not found: {self.model_path}")
            print("Please place your .tflite model file in the model/ directory")
            return False
        
        if not os.path.exists(self.labels_path):
            print(f"Error: Labels file not found: {self.labels_path}")
            print("Please place your labels.txt file in the model/ directory")
            return False
        
        # Initialize camera
        print("Initializing camera...")
        if not self.initialize_camera():
            return False
        
        # Initialize model
        print("Initializing model...")
        if not self.initialize_model():
            return False
        
        # Initialize camera window
        print("Initializing camera window...")
        if not self.initialize_camera_window():
            return False
        
        # Start camera window
        print("Starting camera window...")
        if not self.start_camera_window():
            print("Warning: Camera window failed to start, continuing without it")
        
        # Run detection loop
        try:
            self.run_detection_loop()
        except Exception as e:
            print(f"Error running detection: {e}")
            return False
        
        return True


def main():
    """Main entry point"""
    # Default model paths
    model_path = "model/model.tflite"
    labels_path = "model/labels.txt"
    use_camera_window = False
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--camera-window":
            use_camera_window = True
            if len(sys.argv) > 2:
                model_path = sys.argv[2]
            if len(sys.argv) > 3:
                labels_path = sys.argv[3]
        else:
            model_path = sys.argv[1]
            if len(sys.argv) > 2:
                labels_path = sys.argv[2]
    
    # Create and run controller
    controller = ObjectDetectionController(model_path, labels_path)
    
    if use_camera_window:
        print("Running with camera window...")
        success = controller.run_with_camera_window()
    else:
        success = controller.run()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
