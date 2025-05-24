import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_action(action, message):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(LOG_DIR, f"log_{date_str}.txt")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{time_str}] {action}: {message}\n")
