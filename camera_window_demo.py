#!/usr/bin/env python3
"""
Camera Window Demo
Demonstrates the separate camera window with confidence display
"""

import time
import random
import threading
from camera_window import CameraWindow
from model import ModelLoader


class CameraWindowDemo:
    """Demo class for camera window functionality"""
    
    def __init__(self):
        self.camera_window = None
        self.model = None
        self.is_running = False
        
    def initialize_model(self) -> bool:
        """Initialize the model for detection"""
        try:
            self.model = ModelLoader("model/model.tflite", "model/labels.txt")
            if not self.model.load_model():
                print("Error: Failed to load model")
                return False
            print("Model loaded successfully for camera window demo")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def run_detection_simulation(self):
        """Simulate detection updates for demo purposes"""
        # Sample classes and confidences for demo
        sample_classes = ["crumpled paper", "disposable cup", "plastic bottle", "No detection"]
        
        while self.is_running:
            try:
                # Simulate detection with random confidence
                if random.random() > 0.3:  # 70% chance of detection
                    class_name = random.choice(sample_classes[:-1])  # Exclude "No detection"
                    confidence = random.uniform(0.3, 0.95)
                else:
                    class_name = "No detection"
                    confidence = random.uniform(0.0, 0.3)
                
                # Update camera window with detection
                if self.camera_window:
                    self.camera_window.update_detection(class_name, confidence)
                
                time.sleep(0.5)  # Update every 0.5 seconds
                
            except Exception as e:
                print(f"Error in detection simulation: {e}")
                time.sleep(0.1)
    
    def run_with_model_detection(self):
        """Run camera window with actual model detection"""
        if not self.initialize_model():
            return False
        
        # Create camera window
        self.camera_window = CameraWindow(width=640, height=480, fps=30)
        
        # Start camera window in separate thread
        window_thread = self.camera_window.run_window_threaded()
        
        # Wait a moment for window to start
        time.sleep(2)
        
        self.is_running = True
        print("Camera window with model detection started")
        print("Press 'q' in the camera window to quit")
        
        try:
            while self.is_running and self.camera_window.is_window_running():
                # Get frame from camera
                frame = self.camera_window.camera.get_latest_frame()
                
                if frame is not None and self.model:
                    # Run detection
                    class_name, confidence = self.model.predict(frame)
                    
                    # Update camera window
                    self.camera_window.update_detection(class_name, confidence)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        finally:
            self.is_running = False
            if self.camera_window:
                self.camera_window.stop_camera()
    
    def run_simulation_demo(self):
        """Run camera window with simulated detections"""
        # Create camera window
        self.camera_window = CameraWindow(width=640, height=480, fps=30)
        
        # Start camera window in separate thread
        window_thread = self.camera_window.run_window_threaded()
        
        # Wait a moment for window to start
        time.sleep(2)
        
        self.is_running = True
        print("Camera window with simulated detections started")
        print("Press 'q' in the camera window to quit")
        
        # Start detection simulation in separate thread
        detection_thread = threading.Thread(target=self.run_detection_simulation, daemon=True)
        detection_thread.start()
        
        try:
            while self.is_running and self.camera_window.is_window_running():
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        finally:
            self.is_running = False
            if self.camera_window:
                self.camera_window.stop_camera()
    
    def run(self, mode: str = "simulation"):
        """
        Run the camera window demo
        
        Args:
            mode: "simulation" for simulated detections, "model" for real model detection
        """
        print("Camera Window Demo")
        print("=" * 30)
        
        if mode == "model":
            print("Running with real model detection...")
            self.run_with_model_detection()
        else:
            print("Running with simulated detections...")
            self.run_simulation_demo()


def main():
    """Main demo function"""
    import sys
    
    # Check command line arguments
    mode = "simulation"
    if len(sys.argv) > 1:
        if sys.argv[1] == "model":
            mode = "model"
        elif sys.argv[1] == "simulation":
            mode = "simulation"
        else:
            print("Usage: python3 camera_window_demo.py [simulation|model]")
            print("  simulation: Use simulated detections (default)")
            print("  model: Use real model detection")
            return
    
    # Create and run demo
    demo = CameraWindowDemo()
    demo.run(mode)


if __name__ == "__main__":
    main()
