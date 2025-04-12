from rich.live import Live
from rich.table import Table
import time
from app.data_store import data_store

def generate_table():
    table = Table(title="Bank Statement Live Feed")
    table.add_column("Key")
    table.add_column("Value")
    data = data_store.get_data()
    for k, v in data.items():
        table.add_row(k, str(v))
    return table

def run_dashboard():
    with Live(generate_table(), refresh_per_second=2) as live:
        while True:
            time.sleep(1)
            live.update(generate_table())
