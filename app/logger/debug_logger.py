import csv
import os
from datetime import datetime

LOG_FOLDER = "logs"
DEBUG_HEADERS = ["timestamp", "level", "event"]

os.makedirs(LOG_FOLDER, exist_ok=True)

def get_log_filename():
    today_date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_FOLDER, f"debug_log_{today_date}.csv")

last_log_date = None

def init_debug_log():
    global last_log_date
    current_log_date = datetime.now().strftime("%Y-%m-%d")
    if current_log_date != last_log_date:
        last_log_date = current_log_date
        log_file = get_log_filename()
        if not os.path.exists(log_file):
            with open(log_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=DEBUG_HEADERS)
                writer.writeheader()

def log_debug(message: str, level: str = "INFO"):
    init_debug_log()
    log_file = get_log_filename()
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=DEBUG_HEADERS)
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "event": message
        })
