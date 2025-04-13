import asyncio
from random import uniform
from datetime import datetime
from playwright.async_api import async_playwright
from app.config import BANK_URL, GROUP_ID, LOGIN_ID, PASSWORD, REFRESH_INTERVAL
from app.data_store import data_store
from app.logger.debug_logger import log_debug

MAX_RETRIES = 5
BASE_BACKOFF = 1  # seconds

async def login_and_get_page(context):
    page = await context.new_page()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_debug(f"[Attempt {attempt}] Navigating to bank login page...")

            await page.goto(BANK_URL, wait_until="domcontentloaded")
            log_debug("Bank login page loaded.")

            await page.get_by_role("textbox", name="Group ID").fill(GROUP_ID)
            log_debug("Filled in Group ID.")

            await page.get_by_role("textbox", name="Login ID").fill(LOGIN_ID)
            log_debug("Filled in Login ID.")

            await page.get_by_role("button", name="Login").click()
            log_debug("Clicked 'Login' to proceed to password step.")

            await page.get_by_role("textbox", name="Password").fill(PASSWORD)
            log_debug("Entered password.")

            await page.locator(
                "#frmLogin1 > fieldset > div.panel.panel-default > div > div > div.media-body.media-middle > div > label"
            ).click()
            log_debug("Checked captcha verification box.")

            await page.click('role=button[name="Login"]')
            log_debug("Submitted login credentials.")

            # 🚨 Detect login failure
            try:
                await page.wait_for_timeout(1000)
                error_text = await page.locator("#divPreLogin > div > span").text_content()
                if error_text and "Unable to login" in error_text:
                    log_debug("Login failed: Invalid credentials detected.", level="ERROR")
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    screenshot_path = f"logs/login_fail_attempt_{attempt}_{timestamp}.png"
                    await page.screenshot(path=screenshot_path)
                    log_debug(f"Captured screenshot: {screenshot_path}")

                    raise Exception("Login failed due to invalid credentials.")
            except Exception as e:
                log_debug(f"Error while checking login result: {str(e)}", level="ERROR")
                raise

            # ✅ Proceed with OTP
            otp_field = await page.query_selector('role=textbox[name="OTP"]')
            if otp_field:
                otp = input("Enter OTP: ")
                await otp_field.fill(otp)
                log_debug("Entered OTP from user.")
                await page.click('role=button[name="Submit"]')
                log_debug("Submitted OTP.")
            else:
                log_debug("OTP not required — continuing login.")

            log_debug("Login successful — proceeding to scraping.")
            return page

        except Exception as e:
            log_debug(f"[Attempt {attempt}] Login failed: {str(e)}", level="ERROR")
            backoff = BASE_BACKOFF * (2 ** (attempt - 1)) + uniform(0, 0.5)
            log_debug(f"Retrying login in {backoff:.2f} seconds...")
            await asyncio.sleep(backoff)

    raise Exception("All login attempts failed after retries.")

async def scrape_loop(page):
    while True:
        try:
            log_debug("Running data scraping cycle...")

            element = await page.query_selector("div.account-balance")
            balance = await element.inner_text() if element else "N/A"
            data_store.update_data({"balance": balance})

            log_debug(f"Fetched balance successfully: {balance}")
            await asyncio.sleep(REFRESH_INTERVAL)

        except Exception as e:
            log_debug(f"Error during scraping loop: {str(e)}", level="ERROR")

async def keep_scraping():
    while True:
        try:
            log_debug("Launching browser and initializing scraping loop...")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await login_and_get_page(context)
                await scrape_loop(page)

        except Exception as e:
            log_debug(f"Critical error in keep_scraping loop: {str(e)}", level="ERROR")
            await asyncio.sleep(5)
