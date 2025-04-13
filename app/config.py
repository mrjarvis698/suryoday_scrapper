from dotenv import load_dotenv
import os

load_dotenv()

BANK_URL = os.getenv("BANK_URL")
GROUP_ID = os.getenv("GROUP_ID")
LOGIN_ID = os.getenv("LOGIN_ID")
PASSWORD = os.getenv("PASSWORD")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 5))
