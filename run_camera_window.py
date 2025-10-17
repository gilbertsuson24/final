#!/usr/bin/env python3
"""
Standalone Camera Window Runner
Runs the camera window with confidence display
"""

import sys
import time
from camera_window import CameraWindow
from model import ModelLoader


def main():
    """Run camera window with model detection"""
    print("Camera Window with Confidence Display")
    print("=" * 40)
    
    # Check if model files exist
    model_path = "model/model.tflite"
    labels_path = "model/labels.txt"
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    if len(sys.argv) > 2:
        labels_path = sys.argv[2]
    
    # Initialize model
    print("Loading model...")
    try:
        model = ModelLoader(model_path, labels_path)
        if not model.load_model():
            print("Error: Failed to load model")
            print("Running camera window without detection...")
            model = None
        else:
            print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Running camera window without detection...")
        model = None
    
    # Create camera window
    print("Initializing camera window...")
    camera_window = CameraWindow(width=640, height=480, fps=30)
    
    # Start camera window
    print("Starting camera window...")
    print("Press 'q' in the camera window to quit, 's' to save frame")
    
    try:
        # Start camera window in separate thread
        window_thread = camera_window.run_window_threaded()
        
        # Wait for window to start
        time.sleep(2)
        
        # Main loop for detection updates
        while camera_window.is_window_running():
            try:
                # Get frame from camera
                frame = camera_window.camera.get_latest_frame()
                
                if frame is not None and model:
                    # Run detection
                    class_name, confidence = model.predict(frame)
                    
                    # Update camera window
                    camera_window.update_detection(class_name, confidence)
                elif frame is not None and not model:
                    # No model, show "No detection"
                    camera_window.update_detection("No model loaded", 0.0)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(0.1)
    
    except Exception as e:
        print(f"Error running camera window: {e}")
    
    finally:
        # Cleanup
        camera_window.stop_camera()
        print("Camera window stopped")


if __name__ == "__main__":
    main()
