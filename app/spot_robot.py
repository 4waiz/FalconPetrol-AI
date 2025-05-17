import logging
import os
import time
import json
import torch
import numpy as np
from PIL import Image, ImageDraw
from datetime import datetime
from bosdyn.client import create_standard_sdk
from bosdyn.client.estop import EstopClient, EstopEndpoint, EstopKeepAlive
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive
from bosdyn.client.robot_command import RobotCommandClient, blocking_stand
from bosdyn.client.docking import DockingClient, blocking_dock_robot, blocking_undock
from bosdyn.client.estop import MotorsOnError
from PIL import ImageDraw, ImageFont


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SpotController")
logger.warning("Motors are on; skipping estop force setup.")


class SpotController:
    def __init__(self):
        try:
            self.sdk = create_standard_sdk("FalconPatrol")
            self.robot = self.sdk.create_robot(
                os.getenv("SPOT_IP", "192.168.80.3")
            )
            self.robot.authenticate(
                os.getenv("SPOT_USER", "team1"),
                os.getenv("SPOT_PASSWORD", "team12345678"),
            )
            
            # Initialize E-Stop
            estop_client = self.robot.ensure_client(EstopClient.default_service_name)
            self.estop_endpoint = EstopEndpoint(
                estop_client, "FalconEstop", estop_timeout=9.0
            )
            
            # Force E-Stop setup and start check-in
            try:
                self.estop_endpoint.force_simple_setup()
                logger.info("E-Stop force setup completed")
            except MotorsOnError:
                logger.warning("Motors are on; skipping estop force setup")
            self.estop_keepalive = EstopKeepAlive(self.estop_endpoint)
            logger.info("E-Stop check-in started")

            # Initialize Lease
            self.lease_client = self.robot.ensure_client(LeaseClient.default_service_name)
            self.lease = self.lease_client.take()
            if not self.lease:
                raise RuntimeError("Failed to acquire lease")
            logger.info("Lease acquired successfully")
            self.lease_keepalive = LeaseKeepAlive(self.lease_client)
            logger.info("Lease check-in started")

            # Time sync
            self.robot.time_sync.wait_for_sync()
            logger.info("Time sync established")

            # Power on
            self.robot.power_on(timeout_sec=20)
            logger.info("Robot powered on")

            # Initialize clients
            self.command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)
            self.docking_client = self.robot.ensure_client(DockingClient.default_service_name)

            self._connected = True
            logger.info("SpotController initialized and ready")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            try:
                if hasattr(self, 'robot'):
                    self.robot.power_off(cut_immediately=False)
            except Exception as shutdown_error:
                logger.error(f"Shutdown error: {shutdown_error}")
            raise

    def stand(self, timeout_sec=10):
        with LeaseKeepAlive(self.lease_client):
            blocking_stand(self.command_client, timeout_sec=timeout_sec)
            logger.info("Stand command executed")

    def dock(self, dock_id: int = 520):
        with LeaseKeepAlive(self.lease_client):
            blocking_dock_robot(self.robot, dock_id)
            logger.info(f"Docked at station {dock_id}")

    def undock(self):
        with LeaseKeepAlive(self.lease_client):
            blocking_undock(self.robot)
            logger.info("Undocked successfully")

    def load_yolo_model(self, model_path='yolov5s.pt'):
        try:
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
            logger.info("YOLOv5 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {e}")
            self.yolo_model = None

    def detect_humans_in_image(self, image_np, conf_threshold=0.5):
        logger.debug("Starting human detection")
        if not hasattr(self, 'yolo_model') or self.yolo_model is None:
            logger.error("YOLO model not loaded")
            return []
        try:
            img = Image.fromarray(image_np)
            logger.debug("Image converted from numpy array to PIL Image")

            results = self.yolo_model(img)
            logger.debug("YOLO model inference completed")

            detections = results.xyxy[0].cpu().numpy()  # x1, y1, x2, y2, conf, class
            logger.debug(f"Total detections from model: {len(detections)}")

            humans = []
            for i, (*box, conf, cls) in enumerate(detections):
                logger.debug(f"Detection {i}: class={int(cls)}, conf={conf:.3f}, box={box}")
                if int(cls) == 0 and conf > conf_threshold:
                    bbox_int = [int(coord) for coord in box]
                    logger.debug(f"Detection {i} accepted as human with bbox {bbox_int} and confidence {conf:.3f}")
                    humans.append({
                        "bbox": bbox_int,
                        "confidence": float(conf)
                    })
                else:
                    logger.debug(f"Detection {i} ignored (class or confidence threshold not met)")

            logger.info(f"Detected {len(humans)} humans in total")
            return humans
        except Exception as e:
            logger.error(f"Error during human detection: {e}", exc_info=True)
            return []

    def save_alert_image_with_boxes(self, image_np, humans, save_path):
        logger.debug(f"Saving alert image with {len(humans)} human boxes to {save_path}")
        try:
            img = Image.fromarray(image_np).convert("RGB")
            draw = ImageDraw.Draw(img)

            for i, human in enumerate(humans):
                bbox = human.get("bbox")
                conf = human.get("confidence")
                if bbox and len(bbox) == 4:
                    logger.debug(f"Drawing box {i}: {bbox} with confidence {conf:.3f}")
                    draw.rectangle(bbox, outline="red", width=2)
                    draw.text((bbox[0], bbox[1] - 10), f"Human: {conf:.2f}", fill="red")
                else:
                    logger.warning(f"Skipping invalid bbox at index {i}: {bbox}")

            img.save(save_path)
            logger.info(f"Alert image saved successfully at {save_path}")
        except Exception as e:
            logger.error(f"Failed to save alert image: {e}", exc_info=True)

    def append_alert(self, alert):
        """Append alert dict to alerts.json file."""
        alerts_path = "app/data/alerts.json"
        alerts = []
        if os.path.exists(alerts_path):
            try:
                with open(alerts_path, "r") as f:
                    alerts = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read alerts.json: {e}")

        alerts.append(alert)
        try:
            with open(alerts_path, "w") as f:
                json.dump(alerts, f, indent=4)
            logger.info("Alert appended to alerts.json")
        except Exception as e:
            logger.error(f"Failed to write alerts.json: {e}")

    def load_alerts(self):
        """Load and return alerts from alerts.json."""
        alerts_path = "app/data/alerts.json"
        if not os.path.exists(alerts_path):
            return []

        try:
            with open(alerts_path, "r") as f:
                alerts = json.load(f)
            return alerts
        except Exception as e:
            logger.error(f"Failed to load alerts.json: {e}")
            return []

    def power_off(self, cut_immediately: bool = False):
        self.robot.power_off(cut_immediately=cut_immediately)
        logger.info("Powered off safely")


spot = SpotController()
spot.load_yolo_model()
