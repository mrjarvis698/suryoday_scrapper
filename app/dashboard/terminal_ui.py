from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from datetime import datetime
import time
import os

from app.data_store import data_store

LOG_FILE_PATH = "logs/debug.csv"  # Path to the debug.csv file

def fetch_logs():
    """Fetch the last 10 logs from the debug.csv file."""
    if not os.path.exists(LOG_FILE_PATH):
        return ["Log file not found."]
    
    with open(LOG_FILE_PATH, "r") as file:
        lines = file.readlines()
        logs = [line.strip() for line in lines[-10:]]  # Get the last 10 lines
    return logs

def generate_header():
    """Generate the header with date, time, and project name."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = "Suryoday Automation Project"
    header = Text(f"{current_time} | {project_name}", justify="center", style="bold green")
    return Panel(header, style="bold blue")

def generate_user_inputs():
    """Generate a table for user inputs."""
    table = Table(title="Mini Statement", expand=True)
    table.add_column("Statement", style="bold magenta")
    data = data_store.get_data()  # Assuming user inputs are stored in the data store
    for k, v in data.items():
        table.add_row(k, str(v))
    return Panel(table, style="bold yellow")

def generate_debug_logs():
    """Generate a panel for live debug logs."""
    logs = fetch_logs()  # Fetch live logs from the debug.csv file
    log_text = "\n".join(logs)  # Combine logs into a single string
    return Panel(Text(log_text, style="dim white"), title="Live Debug Logs", style="bold red")

def generate_layout():
    """Generate the overall layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
    )
    layout["body"].split_row(
        Layout(name="debug_logs"),
        Layout(name="user_inputs"),
    )
    layout["header"].update(generate_header())
    layout["user_inputs"].update(generate_user_inputs())
    layout["debug_logs"].update(generate_debug_logs())
    return layout

def run_dashboard():
    """Run the live dashboard."""
    with Live(generate_layout(), refresh_per_second=2) as live:
        while True:
            time.sleep(1)
            live.update(generate_layout())
