from threading import Lock

class DataStore:
    def __init__(self):
        self.lock = Lock()
        self.latest_data = {}

    def update_data(self, data):
        with self.lock:
            self.latest_data = data

    def get_data(self):
        with self.lock:
            return self.latest_data.copy()

data_store = DataStore()
