import torch
import os
import uuid
from datetime import datetime
from PIL import Image
from utils.image_handler import save_alert

# Load YOLO model once
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = 0.4  # confidence threshold
model.classes = [0]  # Only person class

async def detect_humans_and_save(file):
    image = Image.open(file.file).convert("RGB")
    results = model(image)
    detections = results.pandas().xyxy[0]

    human_detections = detections[detections['name'] == 'person']
    saved_alerts = []

    if not human_detections.empty:
        timestamp = datetime.utcnow().isoformat()
        filename = f"{uuid.uuid4().hex}.jpg"
        path = os.path.join("static", "alerts", filename)
        image.save(path)

        alert = {
            "timestamp": timestamp,
            "location": "Zone A",  # customize or infer later
            "image_url": f"/static/alerts/{filename}"
        }

        save_alert(alert)
        saved_alerts.append(alert)

    return saved_alerts
