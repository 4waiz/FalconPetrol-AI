# FalconPatrol AI 🐕💡

FalconPatrol AI is a smart surveillance system using Boston Dynamics Spot Dog and real-time AI detection to monitor restricted areas. It detects unusual human activity, records video, and sends alerts to a cloud dashboard and mobile app.

> Built as part of the NextGen Industry Challenge to support the UAE's vision of smart, secure infrastructure.
[![Watch the video](https://img.youtube.com/vi/KhnNkMcIaIg/maxresdefault.jpg)](https://youtu.be/KhnNkMcIaIg)

---

## 🎯 Features
- 🧠 Real-time AI detection with YOLOv5
- 🤖 Autonomous patrol using Spot Dog
- 📷 Captures and logs intruder activity
- 📲 Fake cloud dashboard + alert system (Streamlit)
- ✅ Easy to demo using local video footage

---

## 🛠️ Tech Stack
| Component     | Tools Used                   |
|---------------|------------------------------|
| AI Detection  | Python, YOLOv5, OpenCV       |
| Dashboard     | Streamlit                    |
| Cloud Sim     | Fake push alert & logs       |
| Video Input   | YouTube test video           |

---

## 🖥️ Run Locally

1. Clone the repo
```bash
git clone https://github.com/4waiz/FalconPetrol-AI.git
cd FalconPetrol-AI/ai_model/yolov5
```
2. Create virtual env and install
```
python3 -m venv venv
source venv/bin/activate
pip install --break-system-packages -r requirements.txt
Add your video as test_video.mp4
```
3. Run detection
```bash
python detect.py --source test_video.mp4 --weights yolov5s.pt --conf 0.5

Extract images 
python extract_frames.py
```

4. Run the dashboard

```bash
streamlit run dashboard.py
```
