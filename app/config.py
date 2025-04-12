from dotenv import load_dotenv
import os

load_dotenv()

BANK_URL = os.getenv("BANK_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 5))
