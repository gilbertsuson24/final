# Model Directory

This directory contains your TensorFlow Lite model and labels for object detection.

## Required Files

Place the following files in this directory:

### 1. model.tflite
- Your exported Teachable Machine model
- Must be in TensorFlow Lite format (.tflite)
- Should be optimized for mobile/embedded devices

### 2. labels.txt
- Text file containing class labels
- One label per line
- Should match the order of classes in your model

## Example labels.txt

```
crumpled paper
disposable cup
plastic bottle
```

## Model Requirements

- **Format**: TensorFlow Lite (.tflite)
- **Input**: RGB images
- **Output**: Classification probabilities
- **Size**: Optimized for Raspberry Pi 5 performance

## Getting Your Model

1. Train your model in Google Teachable Machine
2. Export as TensorFlow Lite model
3. Download the .tflite file and labels.txt
4. Place both files in this directory

## Model Performance Tips

- Use smaller input sizes (224x224 or 299x299) for better performance
- Quantized models run faster on Pi 5
- Avoid very large models (>50MB) for real-time detection
