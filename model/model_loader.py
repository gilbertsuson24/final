"""
TensorFlow Lite Model Loader for Teachable Machine models
"""

import os
import numpy as np
from typing import List, Tuple, Optional
import tflite_runtime.interpreter as tflite


class ModelLoader:
    """Handles loading and running inference on TensorFlow Lite models"""
    
    def __init__(self, model_path: str, labels_path: str):
        """
        Initialize model loader
        
        Args:
            model_path: Path to .tflite model file
            labels_path: Path to .txt labels file
        """
        self.model_path = model_path
        self.labels_path = labels_path
        self.interpreter = None
        self.labels = []
        self.input_details = None
        self.output_details = None
        
    def load_model(self) -> bool:
        """
        Load TensorFlow Lite model and labels
        
        Returns:
            bool: True if model loaded successfully
        """
        try:
            # Check if files exist
            if not os.path.exists(self.model_path):
                print(f"Error: Model file not found: {self.model_path}")
                return False
                
            if not os.path.exists(self.labels_path):
                print(f"Error: Labels file not found: {self.labels_path}")
                return False
            
            # Load TensorFlow Lite model
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Load labels
            with open(self.labels_path, 'r') as f:
                self.labels = [line.strip() for line in f.readlines()]
            
            print(f"Model loaded successfully: {len(self.labels)} classes")
            print(f"Input shape: {self.input_details[0]['shape']}")
            print(f"Output shape: {self.output_details[0]['shape']}")
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image: Input image as numpy array
            
        Returns:
            np.ndarray: Preprocessed image
        """
        # Get expected input shape
        input_shape = self.input_details[0]['shape']
        expected_height, expected_width = input_shape[1], input_shape[2]
        
        # Resize image to expected input size
        resized = cv2.resize(image, (expected_width, expected_height))
        
        # Convert BGR to RGB if needed
        if len(resized.shape) == 3 and resized.shape[2] == 3:
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1] range
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_data = np.expand_dims(normalized, axis=0)
        
        return input_data
    
    def predict(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Run inference on image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple[str, float]: (predicted_class, confidence)
        """
        if self.interpreter is None:
            return "Model not loaded", 0.0
        
        try:
            # Preprocess image
            input_data = self.preprocess_image(image)
            
            # Set input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Get predicted class and confidence
            predicted_class_idx = np.argmax(output_data[0])
            confidence = float(output_data[0][predicted_class_idx])
            
            # Get class name
            if predicted_class_idx < len(self.labels):
                predicted_class = self.labels[predicted_class_idx]
            else:
                predicted_class = "Unknown"
            
            return predicted_class, confidence
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return "Error", 0.0
    
    def get_model_info(self) -> dict:
        """
        Get model information
        
        Returns:
            dict: Model information
        """
        if self.interpreter is None:
            return {}
        
        return {
            'input_shape': self.input_details[0]['shape'],
            'output_shape': self.output_details[0]['shape'],
            'num_classes': len(self.labels),
            'labels': self.labels
        }
    
    def is_loaded(self) -> bool:
        """
        Check if model is loaded
        
        Returns:
            bool: True if model is loaded
        """
        return self.interpreter is not None
