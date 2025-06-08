# AGENTS.md

## Agents Overview

This application uses the following functional agents:

### 1. Plate Detection Agent
- **Purpose**: Detect license plates from camera stream using YOLOv8.
- **Trigger**: New frame from RTSP stream.
- **Action**: Returns bounding boxes and confidence for detected plates.

### 2. OCR Agent
- **Purpose**: Read text from detected plates using EasyOCR.
- **Trigger**: After plate is detected.
- **Action**: Extract alphanumeric text from region of interest.

### 3. Watchlist Checker Agent
- **Purpose**: Match recognized plates against a predefined JSON watchlist.
- **Trigger**: After OCR is complete.
- **Action**: If a match is found, send a webhook.

### 4. Logging Agent
- **Purpose**: Log all detections with timestamp, confidence, and result status.
- **Output**: Saved to /logs and /detected directories.