# main.py

from threading import Thread
from app.playwright_script.live_playwright_script import keep_scraping
from app.dashboard.terminal_ui import run_dashboard
from app.api.app import app  # Import the Flask app
import time

def run_scraping_loop():
    keep_scraping()

def run_flask_api():
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    # Start scraper in its own thread
    scraper_thread = Thread(target=run_scraping_loop, daemon=True)
    scraper_thread.start()

    # Start Flask in its own thread
    flask_thread = Thread(target=run_flask_api, daemon=True)
    flask_thread.start()

    # Start terminal dashboard in main thread
    run_dashboard()
