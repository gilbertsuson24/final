# Raspberry Pi 5 Object Detection System

A Python-based object detection system for Raspberry Pi 5 running Debian Bookworm, using the OV5647 camera module and TensorFlow Lite for real-time object detection. Optimized for OV5647 camera compatibility with rpicam tools.

## Features

- **Live Camera Feed**: Real-time video from OV5647 camera using rpicam
- **TensorFlow Lite Inference**: Fast object detection using exported Teachable Machine models
- **Object Detection**: Detects crumpled paper, disposable cups, plastic bottles, and more
- **Confidence Display**: Shows detection confidence percentages
- **Smooth Detection**: Detection smoothing to reduce flickering
- **Debian Bookworm Compatible**: Optimized for Raspberry Pi 5 with rpicam tools
- **OV5647 Optimized**: Specifically designed for OV5647 camera module compatibility

## Project Structure

```
ROBOT/
├── camera/                 # Camera management module
│   ├── __init__.py
│   └── camera_manager.py  # OV5647 camera handling with rpicam
├── camera_window/          # Camera window module
│   ├── __init__.py
│   └── camera_window.py   # Separate camera window with confidence display
├── model/                 # TensorFlow Lite model directory
│   ├── __init__.py
│   ├── model_loader.py    # Model loading and inference
│   ├── model.tflite      # Your Teachable Machine model (place here)
│   └── labels.txt        # Your model labels (place here)
├── main_controller.py     # Main application controller
├── run_camera_window.py   # Standalone camera window runner
├── camera_window_demo.py  # Camera window demo with simulations
├── camera_diagnostic.py   # Camera diagnostic tool
├── setup_camera.sh        # Automated setup script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Prerequisites

### System Requirements
- Raspberry Pi 5 with Debian Bookworm (Raspberry Pi OS)
- OV5647 camera module
- Python 3.9+ (included with Debian Bookworm)

### Quick Setup

For easy setup, use the provided setup script:

```bash
# Make setup script executable
chmod +x setup_camera.sh

# Run setup script
./setup_camera.sh
```

### Manual System Dependencies

If you prefer manual installation:

```bash
# Update package list
sudo apt update

# Install rpicam-apps (preferred for OV5647)
sudo apt install rpicam-apps

# Install libcamera-tools (fallback option)
sudo apt install libcamera-tools libcamera-dev

# Install OpenCV system dependencies
sudo apt install python3-opencv libopencv-dev

# Install other dependencies
sudo apt install python3-pip python3-venv

# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
```

## Installation

### 1. Clone or Download Project

```bash
# If using git
git clone <repository-url>
cd ROBOT

# Or download and extract the project files
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Alternative: Install individual packages
pip install opencv-python numpy tflite-runtime
```

### 4. Setup Your Model

1. Export your model from Teachable Machine as TensorFlow Lite
2. Place the `.tflite` file in the `model/` directory as `model.tflite`
3. Place the labels file in the `model/` directory as `labels.txt`

Example labels.txt format:
```
crumpled paper
disposable cup
plastic bottle
```

## Usage

### Basic Usage

```bash
# Run with default model paths
python3 main_controller.py

# Run with custom model paths
python3 main_controller.py path/to/your/model.tflite path/to/your/labels.txt

# Run with separate camera window
python3 main_controller.py --camera-window

# Run with custom model paths and camera window
python3 main_controller.py --camera-window path/to/your/model.tflite path/to/your/labels.txt
```

### Camera Window Mode

The camera window mode provides a separate window that displays:
- Live camera feed
- Real-time confidence levels
- Detection status
- Object class information
- Visual confidence bar

```bash
# Run standalone camera window
python3 run_camera_window.py

# Run camera window with custom model
python3 run_camera_window.py path/to/your/model.tflite path/to/your/labels.txt

# Run camera window demo (simulated detections)
python3 camera_window_demo.py simulation

# Run camera window demo (real model detection)
python3 camera_window_demo.py model
```

### Controls

- **'q'**: Quit the application
- **'s'**: Save current frame as image

### Camera Configuration

The system uses the following default settings:
- Resolution: 640x480
- Frame rate: 30 FPS
- Format: MJPEG

You can modify these in `camera/camera_manager.py` if needed.

## Troubleshooting

### Camera Issues

1. **Camera not detected**:
   ```bash
   # Run diagnostic tool
   python3 camera_diagnostic.py
   
   # Test with rpicam (preferred for OV5647)
   rpicam-vid --list-cameras
   
   # Test with libcamera (fallback)
   libcamera-hello --list-cameras
   ```

2. **Permission denied**:
   ```bash
   # Add user to video group
   sudo usermod -a -G video $USER
   # Log out and back in
   ```

3. **OV5647 specific issues**:
   ```bash
   # Ensure camera interface is enabled
   sudo raspi-config
   # Navigate to: Interface Options > Camera > Enable
   
   # Reboot after enabling
   sudo reboot
   
   # Test camera after reboot
   rpicam-vid --list-cameras
   ```

### Model Issues

1. **Model not loading**:
   - Check file paths in `model/` directory
   - Ensure model is compatible with TensorFlow Lite
   - Verify model was exported correctly from Teachable Machine

2. **Low detection accuracy**:
   - Ensure good lighting conditions
   - Check model training quality
   - Adjust confidence threshold in `main_controller.py`

### Performance Issues

1. **Low frame rate**:
   - Reduce camera resolution
   - Increase detection interval
   - Close other applications

2. **High CPU usage**:
   - Use tflite-runtime instead of full TensorFlow
   - Reduce detection frequency
   - Optimize model size

## Configuration

### Detection Parameters

Edit `main_controller.py` to adjust:

```python
# Confidence threshold (0.0 to 1.0)
self.confidence_threshold = 0.5

# Detection interval (seconds)
detection_interval = 0.5

# Detection history smoothing
self.max_history = 10
```

### Camera Settings

Edit `camera/camera_manager.py` to adjust:

```python
# Camera resolution and frame rate
self.width = 640
self.height = 480
self.fps = 30
```

## Development

### Adding New Object Classes

1. Retrain your model in Teachable Machine with new classes
2. Update the labels.txt file with new class names
3. Replace the model.tflite file

### Customizing Detection Display

Edit the `draw_detection_info()` method in `main_controller.py` to customize the display appearance.

## Hardware Compatibility

- **Raspberry Pi 5**: Fully supported
- **Camera Module**: OV5647 (replacement camera for Pi 5)
- **Camera API**: rpicam (preferred) or libcamera (fallback)
- **OS**: Debian Bookworm (Raspberry Pi OS recommended)
- **Python**: 3.9+ (included with Debian Bookworm)

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Test camera and model separately
4. Check system logs for errors

## Performance Notes

- **Expected FPS**: 15-30 FPS depending on model complexity
- **Memory Usage**: ~200-400MB RAM
- **CPU Usage**: 30-60% on Pi 5
- **Detection Latency**: 50-200ms per frame

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on Pi 5
5. Submit a pull request
