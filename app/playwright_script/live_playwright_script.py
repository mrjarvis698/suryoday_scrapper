import asyncio
from random import uniform
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
            log_debug(f"Login attempt {attempt}")

            await page.goto(BANK_URL, wait_until="domcontentloaded")
            log_debug("Navigated to bank URL")

            await page.get_by_role("textbox", name="Group ID").fill(GROUP_ID)
            log_debug("Entered GROUP_ID")

            await page.get_by_role("textbox", name="Login ID").fill(LOGIN_ID)
            log_debug("Entered LOGIN_ID")

            await page.get_by_role("button", name="Login").click()
            log_debug("Phase1: Triggered Login Button")

            await page.get_by_role("textbox", name="Password").fill(PASSWORD)
            log_debug("Entered PASSWORD")

            await page.locator(
                "#frmLogin1 > fieldset > div.panel.panel-default > div > div > div.media-body.media-middle > div > label"
            ).click()
            log_debug("Checked Captcha Checkbox")

            await page.click('role=button[name="Login"]')
            log_debug("Phase2: Triggered Login Button")

            # 🚨 Detect login failure
            try:
                await page.wait_for_timeout(1000)  # Wait briefly for error to appear
                error_text = await page.locator("#divPreLogin > div > span").text_content()
                if error_text and "Unable to login" in error_text:
                    log_debug("Login failed: Invalid credentials", level="ERROR")
                    await page.screenshot(path=f"logs/login_fail_attempt_{attempt}.png")
                    raise Exception("Login failed due to invalid credentials.")
            except Exception as e:
                log_debug(f"Login check error: {str(e)}", level="ERROR")
                raise  # Triggers retry
            
            # ✅ Only if login was successful
            otp_field = await page.query_selector('role=textbox[name="OTP"]')

            #TODO: check this with exceptions
            if otp_field:
                otp = input("Enter OTP: ")
                await otp_field.fill(otp)
                log_debug("Entered OTP")
                await page.click('role=button[name="Submit"]')
                log_debug("Final Login Submit")
            else:
                log_debug("No OTP field found, continuing.")

            log_debug("Login successful")
            return page  # ✅ Login complete, continue to scrape

        except Exception as e:
            log_debug(f"Login attempt {attempt} failed: {str(e)}", level="ERROR")
            backoff = BASE_BACKOFF * (2 ** (attempt - 1)) + uniform(0, 0.5)
            log_debug(f"Retrying in {backoff:.2f} seconds...")
            await asyncio.sleep(backoff)

    raise Exception("All login attempts failed.")

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
