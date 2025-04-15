import asyncio
from threading import Thread
from app.playwright_script.live_playwright_script import keep_scraping
from app.dashboard.terminal_ui import run_dashboard
from app.data_store import data_store

def run_scraping_loop():
    # This function runs the scraping loop and updates the data store with live data
    async def scraping_task():
        await keep_scraping()  # Start the scraping process
    asyncio.run(scraping_task())

if __name__ == "__main__":
    # Start the scraping loop in a separate thread
    scraper_thread = Thread(target=run_scraping_loop, daemon=True)
    scraper_thread.start()

    # Run the terminal dashboard to display live updates
    run_dashboard()
