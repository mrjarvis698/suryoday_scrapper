import asyncio
from playwright.async_api import async_playwright
from app.config import BANK_URL, USERNAME, PASSWORD, REFRESH_INTERVAL
from app.data_store import data_store
from app.logger.debug_logger import log_debug

async def login_and_get_page(context):
    log_debug("Starting login flow")
    page = await context.new_page()
    await page.goto(BANK_URL)
    log_debug("Navigated to bank URL")
    await page.fill('input[name="username"]', USERNAME)
    await page.fill('input[name="password"]', PASSWORD)
    await page.click('button[type="submit"]')
    await page.wait_for_selector("div.account-summary")
    log_debug("Login successful")
    return page

async def scrape_loop(page):
    while True:
        try:
            log_debug("Starting scrape loop")
            element = await page.query_selector("div.account-balance")
            balance = await element.inner_text() if element else "N/A"
            data_store.update_data({"balance": balance})
            log_debug(f"Scraped balance: {balance}")
            await asyncio.sleep(REFRESH_INTERVAL)
        except Exception as e:
            log_debug(f"Error in scrape loop: {str(e)}", level="ERROR")

async def keep_scraping():
    while True:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await login_and_get_page(context)
                await scrape_loop(page)
        except Exception as e:
            log_debug(f"Fatal error in keep_scraping: {str(e)}", level="ERROR")
            await asyncio.sleep(5)
