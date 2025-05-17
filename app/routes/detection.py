from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import io
import logging
from datetime import datetime
import os

router = APIRouter()

@router.post("/detect_humans")
async def detect_humans(request: Request, file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(img)

        spot = request.app.state.spot
        if not spot or not hasattr(spot, 'yolo_model'):
            raise HTTPException(status_code=500, detail="SpotController or YOLO model not initialized")

        humans = spot.detect_humans_in_image(image_np)
        return JSONResponse(content={"detections": humans})

    except Exception as e:
        logging.error(f"Human detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect_and_save_alert")
async def detect_and_save_alert(request: Request, file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(img)

        spot = request.app.state.spot
        if not spot or not hasattr(spot, 'yolo_model'):
            raise HTTPException(status_code=500, detail="SpotController or YOLO model not initialized")

        # Detect humans
        humans = spot.detect_humans_in_image(image_np)

        # If humans detected, save alert
        if humans:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            alert_img_name = f"alert_{timestamp}.jpg"
            alert_img_path = os.path.join("app/static/alerts", alert_img_name)

            # Save image with bounding boxes
            spot.save_alert_image_with_boxes(image_np, humans, alert_img_path)

            # Create alert dict
            alert = {
                "imageUrl": f"/static/alerts/{alert_img_name}",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": "Spot Front Camera",
                "description": f"{len(humans)} person(s) detected"
            }

            # Append alert to alerts.json
            spot.append_alert(alert)

            return JSONResponse(content={"message": "Alert saved", "alert": alert})

        return JSONResponse(content={"message": "No humans detected"})

    except Exception as e:
        logging.error(f"Detection and alert save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(request: Request):
    try:
        spot = request.app.state.spot
        if not spot:
            raise HTTPException(status_code=500, detail="SpotController not initialized")

        alerts = spot.load_alerts()
        return JSONResponse(content={"alerts": alerts})

    except Exception as e:
        logging.error(f"Get alerts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
