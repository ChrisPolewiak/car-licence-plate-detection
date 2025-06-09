import os
import sys
import ctypes
import contextlib
import cv2
import json
import time
import requests
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ultralytics import YOLO
import easyocr
import logging

os.environ["KMP_WARNINGS"] = "0"  # jeśli używasz torch
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.stderr = open(os.devnull, 'w')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/detection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger("easyocr").setLevel(logging.WARNING)
logging.getLogger("ultralytics").setLevel(logging.WARNING)


try:
    import tqdm
    tqdm.tqdm.__init__ = lambda *a, **k: None  # hard kill if needed
except:
    pass

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv()
RTSP_URL = os.getenv("RTSP_URL")
HASSIO_WEBHOOK = os.getenv("HASSIO_WEBHOOK")
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL")

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("detected", exist_ok=True)

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

import torch
from ultralytics.nn.tasks import DetectionModel
from torch.serialization import safe_globals


from ultralytics import YOLO

try:
    model = torch.jit.load("best.torchscript.pt", map_location="cpu").eval()
except Exception as e:
    logging.exception("Failed to load YOLO TorchScript model")
    sys.exit(1)

try:
    reader = easyocr.Reader(['en'], gpu=False)
except Exception as e:
    logging.exception("Failed to initialize EasyOCR reader")
    sys.exit(1)

def process_frame(frame):

    frame_resized = cv2.resize(frame, (640, 640))
    img_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1).float().div(255.0).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)[0].cpu().numpy()

    for det in output:
        x1, y1, x2, y2, conf, cls = det[:6]
        if conf < CONFIDENCE_THRESHOLD:
            continue

        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        img_crop = frame[y1:y2, x1:x2]
        if img_crop is None or img_crop.shape[0] == 0 or img_crop.shape[1] == 0:
            continue

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

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    logging.info("Starting plate detection from RTSP stream: %s", RTSP_URL)
    
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        logging.error("Failed to open RTSP stream")
        return

    frame_counter = 0
    last_report_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.warning("Failed to read frame")
            time.sleep(1)
            continue

        frame_counter += 1
        process_frame(frame)

        if time.time() - last_report_time > 300:  # 5 minut
            logging.info(f"Processed frames so far: {frame_counter}")
            last_report_time = time.time()

    cap.release()

if __name__ == "__main__":
    logging.info("Starting plate detector (CPU-only)...")
    main()