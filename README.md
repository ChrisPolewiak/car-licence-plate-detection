# Car License Plate Detection (CPU-only, Synology-ready)

YOLOv8 + EasyOCR based license plate detection app, designed for use on CPU-only environments such as Synology NAS.  
Detects license plates from an RTSP stream, matches against a watchlist, saves logs and image snapshots, and sends webhook notifications (e.g. to Home Assistant).

---

## 🚀 Features

- 📹 RTSP stream input (e.g. from IP camera or Synology Surveillance Station)
- 🔍 YOLOv8 + EasyOCR-based license plate detection
- 🧠 Watchlist-based matching (`plates_watchlist.json`)
- 📤 Webhook integration (e.g. Home Assistant)
- 🧾 Logging to file (`logs/detection.log`)
- 🖼️ Saves detection snapshots to `/detected/`
- 🐳 Deployable via Docker or Docker Compose (CPU-only)

---

## ⚙️ Getting Started

```bash
git clone https://github.com/ChrisPolewiak/car-licence-plate-detection.git
cd car-licence-plate-detection
cp .env.template .env
# Edit .env to configure RTSP stream, webhook and paths
docker compose build
docker compose up -d


## 📦 Model Source

This application uses a pre-trained YOLOv8 model (`best.pt`) and base code structure from the following open-source project:

**Automatic Plate Detection Using YOLOv8**  
GitHub: [https://github.com/gorkemturkut57/Automatic_Plate_Detection_Using_YoloV8](https://github.com/gorkemturkut57/Automatic_Plate_Detection_Using_YoloV8)

This repository provides a complete training and inference pipeline using the [CCPD (Chinese City Parking Dataset)](https://github.com/detectRecog/CCPD) dataset.

We acknowledge and thank the original author [@gorkemturkut57](https://github.com/gorkemturkut57) for sharing both code and the model.

📌 You can replace `best.pt` with your own YOLOv8-trained model adapted to your region's license plate format.
