import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.routes import detection
import torch
import numpy as np
from PIL import Image
from fastapi import UploadFile, File
import io
from datetime import datetime
from .spot_robot import SpotController  # Assuming spot_robot.py is in the same folder
# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("robot.log"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("SpotApp")

app = FastAPI()


# Serve static files (if any)
app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")
app.mount("/alerts_images", StaticFiles(directory="app/data/alerts_images"), name="alerts_images")


# Include detection routes
app.include_router(detection.router)

# Allow all origins for simplicity (lock down in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Error"],
)

# Global SpotController instance
spot: SpotController = None

@app.on_event("startup")
def startup_event():
    global spot
    try:
        spot = SpotController()
        spot.load_yolo_model()  # <--- Add this line!
        app.state.spot = spot
        logger.info("SpotController initialized and YOLO model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SpotController or load model: {e}")
        raise


@app.on_event("shutdown")
def shutdown_event():
    global spot
    try:
        if spot:
            spot.power_off(cut_immediately=False)  # Safe shutdown
            logger.info("Spot powered off safely on shutdown")
    except Exception as e:
        logger.error(f"Error during Spot shutdown: {e}")

@app.get("/stand")
def stand():
    try:
        spot.stand()
        return {"message": "Spot is standing"}
    except Exception as e:
        logger.error(f"Stand command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dock")
def dock(dock_id: int = None):
    try:
        if dock_id is None:
            spot.dock()  # Use default dock station
        else:
            spot.dock(dock_id)
        return {"message": "Spot is docking"}
    except Exception as e:
        logger.error(f"Dock command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/undock")
def undock():
    try:
        spot.undock()
        return {"message": "Spot is undocking"}
    except Exception as e:
        logger.error(f"Undock command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/poweroff")
def power_off():
    try:
        spot.power_off(cut_immediately=False)
        return {"message": "Spot is powering off"}
    except Exception as e:
        logger.error(f"Power off command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/detect_and_save_alert")
async def detect_and_save_alert(file: UploadFile = File(...)):
    global spot
    if not spot:
        raise HTTPException(status_code=500, detail="SpotController not initialized")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image_np = np.array(image)

    humans = spot.detect_humans_in_image(image_np)
    if len(humans) == 0:
        return {"message": "No humans detected"}

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"alert_{timestamp}.jpg"
    save_dir = "app/data/alerts_images"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    spot.save_alert_image_with_boxes(image_np, humans, save_path)

    alert = {
        "timestamp": timestamp,
        "image_path": save_path,
        "num_humans": len(humans),
        "humans": humans,
        "image_url": f"/alerts_images/{filename}",
    }

    spot.append_alert(alert)

    return alert
@app.get("/get_alerts")
def get_alerts():
    global spot
    alerts = spot.load_alerts()
    for alert in alerts:
        filename = os.path.basename(alert["image_path"])
        alert["image_url"] = f"/alerts_images/{filename}"
    return alerts


@app.get("/logs")
async def get_logs():
    try:
        with open("robot.log", "r") as f:
            logs = f.read()
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to read logs"})
