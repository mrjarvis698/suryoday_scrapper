# app/app.py

from flask import Flask, jsonify
from app.data_store import data_store

app = Flask(__name__)

@app.route("/mini-statement", methods=["GET"])
def get_mini_statement():
    if data_store.get_data():
        return data_store.get_data()
    else:
        return jsonify({"error": "No mini-statement data available yet"}), 404
