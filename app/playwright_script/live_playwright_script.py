import time
from random import uniform
from datetime import datetime
from playwright.sync_api import sync_playwright
from app.config import BANK_URL, GROUP_ID, LOGIN_ID, PASSWORD, REFRESH_INTERVAL
from app.data_store import data_store
from app.logger.debug_logger import log_debug
import tkinter as tk
from tkinter import messagebox
import json

MAX_RETRIES = 5
BASE_BACKOFF = 1  # seconds

# Shared data to expose to the API
json_formatted_str = None

def get_otp_via_gui():
    # Create the main window (root)
    root = tk.Tk()
    root.title("OTP Input")

    # Set the window to always stay on top and set a fixed size
    root.attributes('-topmost', True)
    root.geometry('300x200')  # Window size (width x height)
    root.resizable(False, False)  # Disable resizing

    # Styling for the window and widgets
    root.config(bg="#f0f0f0")

    # Label for OTP
    otp_label = tk.Label(root, text="Please enter your OTP:", font=("Arial", 12), bg="#f0f0f0")
    otp_label.pack(pady=20)

    # OTP Entry widget with a restriction to allow only digits and 6 characters
    otp_entry = tk.Entry(root, font=("Arial", 14), width=20, justify='center', bd=2, relief="solid")
    otp_entry.pack(pady=10)

    otp_value = None

    # Function to validate OTP input
    def validate_otp_input(event):
        value = otp_entry.get()

        # Restrict to only digits and max length of 6
        if not value.isdigit() or len(value) > 6:
            otp_entry.delete(0, tk.END)  # Clear the field
            messagebox.showerror("Invalid OTP", "OTP must be 6 digits long and contain only numbers.")
        elif len(value) == 6:
            otp_entry.config(fg="green")  # Change text color to green when 6 digits are entered

    otp_entry.bind("<KeyRelease>", validate_otp_input)

    # Function to handle the Submit action
    def on_submit():
        nonlocal otp_value
        otp_value = otp_entry.get()

        if len(otp_value) == 6:  # Check if OTP is exactly 6 digits long
            root.quit()  # This will exit the main loop and close the window
            root.destroy()  # Explicitly destroy the window to ensure proper closure
        else:
            messagebox.showerror("Invalid OTP", "OTP must be exactly 6 digits long.")

    # Submit Button
    submit_button = tk.Button(root, text="Submit", font=("Arial", 12), bg="#4CAF50", fg="white", command=on_submit, width=15)
    submit_button.pack(pady=20)

    # Start the Tkinter event loop, suspending the process until Submit is clicked
    root.mainloop()

    return otp_value

def login_and_get_page(context):
    page = context.new_page()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_debug(f"[Attempt {attempt}] Navigating to bank login page...")

            page.goto(BANK_URL, wait_until="domcontentloaded")
            log_debug("Bank login page loaded.")

            page.locator('role=textbox[name="Group ID"]').fill(GROUP_ID)
            log_debug("Filled in Group ID.")

            page.locator('role=textbox[name="Login ID"]').fill(LOGIN_ID)
            log_debug("Filled in Login ID.")

            page.locator('role=button[name="Login"]').click()
            log_debug("Clicked 'Login' to proceed to password step.")

            page.locator('role=textbox[name="Password"]').fill(PASSWORD)
            log_debug("Entered password.")

            page.locator(
                "#frmLogin1 > fieldset > div.panel.panel-default > div > div > div.media-body.media-middle > div > label"
            ).click()
            log_debug("Checked captcha verification box.")

            page.locator('role=button[name="Login"]').click()
            log_debug("Submitted login credentials.")

            # 🚨 Detect login failure
            try:
                # Wait for timeout before checking for errors
                #page.wait_for_timeout(1000)

                # Check if the login failed due to invalid credentials
                if "Enter OTP" in page.get_by_text("Enter OTP").text_content():                    
                    log_debug("Asking for OTP Please provide OTP.")                    
                    # Prompt for OTP input and fill the OTP field
                    otp = get_otp_via_gui()
                    page.locator('role=textbox[name="OTP"]').fill(otp)
                    log_debug("Provided OTP from GUI.") 
                    page.get_by_role("button", name="Submit").click()
                    log_debug("Submitted OTP.") 
                    if "Dashboard" in page.locator("h3").text_content():
                        log_debug("Login successful able to view Dashboard.")
                        page.locator("css=#accounts > p:nth-child(2)").click()
                        log_debug("Clicked on the accounts card in dashboard.")
                        page.locator("#mnuAccountStatement").click()
                        log_debug("Clicked on the account statement tab.")
                        
                        page.locator("iframe[name=\"icanvas\"]").content_frame.locator("#accountId_chosen > a > span").click()
                        log_debug("Clicked on the 'Choose and option' dropdown.")
                        page.locator("iframe[name=\"icanvas\"]").content_frame.locator("#accountId_chosen > div > ul > li.active-result.group-option").click()
                        log_debug("Selected on the user's account from the dropdown.")                        
                    else:                        
                        # Capture a screenshot of the failed login attempt
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        screenshot_path = f"logs/login_fail_attempt_{attempt}_{timestamp}.png"
                        log_debug(f"Login failed: Dashboard is not visible. View for more clear info {screenshot_path}", level="ERROR")
                        page.screenshot(path=screenshot_path)
                        log_debug(f"Captured screenshot: {screenshot_path}")
                        raise Exception("Login failed due to invalid OTP.")
                else:
                    log_debug("Login failed: Invalid credentials detected.", level="ERROR")

                    # Capture a screenshot of the failed login attempt
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    screenshot_path = f"logs/login_fail_attempt_{attempt}_{timestamp}.png"
                    page.screenshot(path=screenshot_path)
                    log_debug(f"Captured screenshot: {screenshot_path}")

                    raise Exception("Login failed due to invalid credentials.")
            
            except Exception as e:
                log_debug(f"Error while checking login result: {str(e)}", level="ERROR")
                raise
            '''

            otp_field = page.locator('role=textbox[name="OTP"]')
            if otp_field:
                # Prompt user to enter OTP
                otp = input("Enter OTP: ")
                if not otp:  # If OTP is not entered, login should fail
                    log_debug("OTP is required, but none entered. Aborting login.", level="ERROR")
                    raise Exception("OTP is required but not provided. Login failed.")

                otp_field.fill(otp)
                log_debug("Entered OTP from user.")
                page.locator('role=button[name="Submit"]').click()
                log_debug("Submitted OTP.")
            else:
                log_debug("OTP field is missing, which is not expected. Login failed.", level="ERROR")
                raise Exception("OTP field is missing, login failed.")
                
            '''

            log_debug("Login successful — proceeding to fetch data.")
            return page

        except Exception as e:
            log_debug(f"[Attempt {attempt}] Login failed: {str(e)}", level="ERROR")
            backoff = BASE_BACKOFF * (2 ** (attempt - 1)) + uniform(0, 0.5)
            log_debug(f"Retrying login in {backoff:.2f} seconds...")
            time.sleep(backoff)

    raise Exception("All login attempts failed after retries.")

def scrape_loop(page):
    while True:
        global json_formatted_str
        try:
            log_debug("Running statement cycle...")
            account_id= page.locator("iframe[name=\"icanvas\"]").content_frame.locator("#accountId > optgroup > option").get_attribute('value')
            js_code = f"""
            (async () => {{
                const testAccountId = "{account_id}";
                $("#accountId").val(testAccountId);
                $("#accountId").trigger("change");

                const response = await new Promise((resolve, reject) => {{
                    $.ajax({{
                        type: 'POST',
                        url: getURL("/Corporate/account/statement/mini"),
                        data: {{ "id": testAccountId }},
                        headers: {{
                            'Accept': 'text/html'
                        }},
                        success: function (data, textStatus, jqXHR) {{
                            const contentType = jqXHR.getResponseHeader('Content-Type');
                            if (contentType && contentType.includes('text/html')) {{
                                const parser = new DOMParser();
                                const doc = parser.parseFromString(jqXHR.responseText, 'text/html');
                                const rows = doc.querySelectorAll("#stmtTableDiv table tbody tr");
                                const transactions = [];
                                rows.forEach(row => {{
                                    const cells = row.querySelectorAll("td");
                                    transactions.push({{
                                        transactionDate: cells[0]?.textContent.trim(),
                                        valueDate: cells[1]?.textContent.trim(),
                                        referenceNo: cells[2]?.textContent.trim(),
                                        remarks: cells[3]?.textContent.trim(),
                                        debitCredit: cells[4]?.textContent.trim(),
                                        transactionAmount: cells[5]?.textContent.trim(),
                                        availableBalance: cells[6]?.textContent.trim()
                                    }});
                                }});
                                resolve(transactions);
                            }} else {{
                                reject("Unexpected content type: " + contentType);
                            }}
                        }},
                        error: function (xhr, status, error) {{
                            reject("AJAX error: " + error + " (Status: " + xhr.status + ")");
                        }}
                    }});
                }});

                return response;
            }})()
            """
            json_formatted_str = json.dumps(page.evaluate(js_code))
            # Update the data store with the scraped data
            data_store.update_data({"balance": json_formatted_str})

            log_debug(f"Fetched balance successfully: {json_formatted_str}")
            time.sleep(REFRESH_INTERVAL)

        except Exception as e:
            log_debug(f"Error during scraping loop, will restart login: {str(e)}", level="ERROR")
            # Capture a screenshot of the failed login attempt
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = f"logs/login_fail_loop_attempt_{timestamp}.png"
            page.screenshot(path=screenshot_path)
            log_debug(f"Captured screenshot: {screenshot_path}")
            raise  # Important: re-raise the error to trigger a fresh login

def keep_scraping():
    while True:
        try:
            log_debug("Launching browser and initializing scraping loop...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = login_and_get_page(context)

                # Start the scraping loop
                scrape_loop(page)

        except Exception as e:
            log_debug(f"Critical error in keep_scraping loop: {str(e)}", level="ERROR")
            
            time.sleep(5)
