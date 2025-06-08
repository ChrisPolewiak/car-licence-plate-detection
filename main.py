import os
import contextlib
import cv2
import json
import time
import requests
import numpy as np
import sys
from PIL import Image
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ultralytics import YOLO
import easyocr
from torch.serialization import add_safe_classes
from ultralytics.nn.tasks import DetectionModel

# Load environment variables
load_dotenv()
RTSP_URL = os.getenv("RTSP_URL")
HASSIO_WEBHOOK = os.getenv("HASSIO_WEBHOOK")
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL")

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("detected", exist_ok=True)

import logging

# Configure logging
logging.basicConfig(
    filename="logs/detection.log",
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Load watchlist
with open("plates_watchlist.json", "r") as f:
    watchlist_data = json.load(f)
WATCHLIST = watchlist_data.get("plates", {})
THROTTLE_SECONDS = 60
last_sent = {}

CONFIDENCE_THRESHOLD = 0.75

def send_webhook(plate, label, confidence, image_path):
    timestamp = datetime.now().isoformat()
    image_url = f"{IMAGE_BASE_URL}/detected/{image_path}"
    payload = {
        "plate": plate,
        "label": label,
        "confidence": confidence,
        "timestamp": timestamp,
        "image_url": image_url
    }
    try:
        requests.post(HASSIO_WEBHOOK, json=payload, timeout=5)
        logging.info(f"Webhook sent for {plate}: {payload}")
    except Exception as e:
        logging.error(f"Failed to send webhook for {plate}: {e}")

@contextlib.contextmanager
def suppress_stdout():
    with contextlib.redirect_stdout(open(os.devnull, 'w')):
        yield



add_safe_classes([DetectionModel])
model = YOLO("best.pt").to("cpu")
with suppress_stdout():
    reader = easyocr.Reader(['en'], gpu=False)

def process_frame(frame):

    results = model(frame)
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box.tolist())
            img_crop = frame[y1:y2, x1:x2]
            ocr_results = reader.readtext(img_crop)

            result_text = ""
            max_conf = 0.0
            for detection in ocr_results:
                text = detection[1].replace(" ", "").upper()
                conf = detection[2]
                result_text += text
                max_conf = max(max_conf, conf)

            if max_conf < CONFIDENCE_THRESHOLD:
                continue

            plate = result_text.replace("-", "")
            label = WATCHLIST.get(plate)

            # Save cropped image
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{plate}_{timestamp_str}.jpg"
            cv2.imwrite(os.path.join("detected", image_filename), img_crop)

            log_msg = f"Detected plate: {plate}, confidence: {int(max_conf * 100)}%"
            if label:
                log_msg += f", label: {label}"
            logging.info(log_msg)

            if label:
                last_time = last_sent.get(plate)
                now = datetime.now()
                if not last_time or (now - last_time) > timedelta(seconds=THROTTLE_SECONDS):
                    send_webhook(plate, label, int(max_conf * 100), image_filename)
                    last_sent[plate] = now

def main():
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        logging.error("Failed to open RTSP stream")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.warning("Failed to read frame")
            time.sleep(1)
            continue

        process_frame(frame)

    cap.release()

if __name__ == "__main__":
    print("Starting plate detector (CPU-only)...")
    main()