"""
Camera Manager for OV5647 camera module on Raspberry Pi 5
Compatible with Debian Trixie using libcamera tools
"""

import subprocess
import threading
import time
import cv2
import numpy as np
from typing import Optional, Tuple


class CameraManager:
    """Manages OV5647 camera using libcamera for live video feed"""
    
    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        """
        Initialize camera manager
        
        Args:
            width: Camera resolution width
            height: Camera resolution height  
            fps: Frames per second
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.is_running = False
        self.current_frame = None
        self.camera_process = None
        self.frame_lock = threading.Lock()
        
    def start_camera(self) -> bool:
        """
        Start camera using libcamera-vid
        
        Returns:
            bool: True if camera started successfully
        """
        try:
            # Check if libcamera-vid is available
            result = subprocess.run(['which', 'libcamera-vid'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("Error: libcamera-vid not found. Please install libcamera-tools")
                return False
            
            # Start libcamera-vid process with output to stdout
            cmd = [
                'libcamera-vid',
                '--width', str(self.width),
                '--height', str(self.height),
                '--framerate', str(self.fps),
                '--output', '-',  # Output to stdout
                '--codec', 'mjpeg',
                '--timeout', '0',  # Run indefinitely
                '--nopreview'
            ]
            
            self.camera_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            self.is_running = True
            print(f"Camera started: {self.width}x{self.height} @ {self.fps}fps")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera and cleanup resources"""
        self.is_running = False
        
        if self.camera_process:
            self.camera_process.terminate()
            try:
                self.camera_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.camera_process.kill()
            self.camera_process = None
        
        print("Camera stopped")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get current frame from camera
        
        Returns:
            np.ndarray: Current frame or None if not available
        """
        if not self.is_running or not self.camera_process:
            return None
            
        try:
            # Read frame data from libcamera-vid stdout
            if self.camera_process.poll() is None:
                # Read MJPEG frame from libcamera-vid
                frame_data = self.camera_process.stdout.read(1024 * 1024)  # 1MB buffer
                if frame_data:
                    # Convert bytes to numpy array
                    nparr = np.frombuffer(frame_data, np.uint8)
                    # Decode MJPEG frame
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        with self.frame_lock:
                            self.current_frame = frame
                        return frame
        except Exception as e:
            print(f"Error reading frame: {e}")
            
        return None
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest captured frame
        
        Returns:
            np.ndarray: Latest frame or None
        """
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def is_camera_available(self) -> bool:
        """
        Check if camera is available and working
        
        Returns:
            bool: True if camera is available
        """
        try:
            # Test camera availability using libcamera-hello
            result = subprocess.run(['libcamera-hello', '--list-cameras'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.start_camera()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_camera()
