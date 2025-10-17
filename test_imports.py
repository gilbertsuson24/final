#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import cv2
        print("✓ OpenCV imported successfully")
        
        import numpy as np
        print("✓ NumPy imported successfully")
        
        # Test model loader import
        from model import ModelLoader
        print("✓ ModelLoader imported successfully")
        
        # Test camera manager import
        from camera import CameraManager
        print("✓ CameraManager imported successfully")
        
        # Test main controller import
        from main_controller import ObjectDetectionController
        print("✓ ObjectDetectionController imported successfully")
        
        print("\n✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if not success:
        exit(1)
