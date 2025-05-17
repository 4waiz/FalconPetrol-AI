import json
import os

DATA_FILE = "app/static/alerts"

def save_alert(alert):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    with open(DATA_FILE, "r+") as f:
        data = json.load(f)
        data.insert(0, alert)  # latest first
        f.seek(0)
        json.dump(data[:100], f, indent=2)  # keep last 100 entries

def get_recent_alerts(limit=5):
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        return data[:limit]
