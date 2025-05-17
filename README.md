# FalconPatrol AI 🐕💡

FalconPatrol AI is a smart surveillance system using Boston Dynamics Spot Dog and real-time AI detection to monitor restricted areas. It detects unusual human activity, records video, and sends alerts to a cloud dashboard and mobile app.

> Built as part of the NextGen Industry Challenge to support the UAE's vision of smart, secure infrastructure.
[![Watch the video](https://img.youtube.com/vi/KhnNkMcIaIg/maxresdefault.jpg)](https://youtu.be/KhnNkMcIaIg)

---

## 🎯 Features
- 🧠 Real-time AI detection with YOLOv5 (Human detection)
- 🤖 Remote control of Boston Dynamics Spot robot (Dock/Undock, Stand/Sit, Move)
- 📷 Captures and logs intruder activity with timestamp, image & location
- 🌐 Web dashboard built with React + FastAPI backend
- ☁️ Simulated cloud alert system with local logs (Alert Log)

---

## 🛠️ Tech Stack

| Component     | Tools Used                           |
| ------------- | ------------------------------------ |
| Backend API   | Python, FastAPI, Boston Dynamics SDK |
| Frontend UI   | React, Tailwind CSS                  |
| AI Detection  | YOLOv5, OpenCV, Torch                |
| Robot Control | Spot SDK: Estop, Lease, Docking APIs |
| Image Logging | Local Storage (Saved Alerts)         |

---

## 🖥️ Run Locally

🔧 1. Clone the repository
```
git clone https://github.com/4waiz/FalconPetrol-AI.git
cd FalconPetrol-AI
```
🐍 2. Set up Python virtual environment
```
python3 -m venv venv
source venv/bin/activate
pip install --break-system-packages -r requirements.txt
```
3. 🚀 Start the FastAPI Backend
```
run in your venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. 🌐 Start the React Frontend

```
In terminal 2
cd frontend
npm install
npm run dev
```
