from flask import Flask, jsonify
from app.data_store import data_store

app = Flask(__name__)

@app.route("/api/data")
def get_data():
    return jsonify(data_store.get_data())
