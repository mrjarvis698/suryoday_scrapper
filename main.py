import asyncio
from threading import Thread
from app.playwright_script.live_playwright_script import keep_scraping
from app.dashboard.terminal_ui import run_dashboard

def run_scraping_loop():
    asyncio.run(keep_scraping())

if __name__ == "__main__":
    scraper_thread = Thread(target=run_scraping_loop, daemon=True)
    scraper_thread.start()
    run_dashboard()
