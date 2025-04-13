import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, "debug.csv")

# Define CSV log format
class CSVFormatter(logging.Formatter):
    def format(self, record):
        log_time = datetime.fromtimestamp(record.created)
        date = log_time.strftime("%Y-%m-%d")
        time = log_time.strftime("%H:%M:%S")
        level = record.levelname
        message = record.getMessage().replace("\n", " ").replace(",", ";")  # Avoid breaking CSV
        return f"{date},{time},{level},{message}"

# Setup logger
logger = logging.getLogger("playwright_script_logger")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = TimedRotatingFileHandler(
        LOG_FILE_PATH,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    handler.setFormatter(CSVFormatter())
    handler.suffix = "%Y-%m-%d"
    logger.addHandler(handler)

# Ensure headers are present
if not os.path.isfile(LOG_FILE_PATH) or os.stat(LOG_FILE_PATH).st_size == 0:
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write("Date,Time,Error Level,Logs\n")

def log_debug(message, level="INFO"):
    if level == "DEBUG":
        logger.debug(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)
