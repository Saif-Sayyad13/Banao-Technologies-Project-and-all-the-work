"""Kestrel routing service.   python app.py   ->  http://localhost:8000
POST /route  {"request_text": "...", "channel": "chat", "warranty_status": "in_warranty", "product_family": "Air Fryer"}
No API key, no internet, no per-request cost."""
import os
from flask import Flask, jsonify, request, send_from_directory
from kestrel.service import route
from kestrel.text import TEAMS

app = Flask(__name__, static_folder="static")
CHANNELS = ["ivr", "chat", "whatsapp", "email"]
WARRANTY = ["in_warranty", "shield", "out_of_warranty"]


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/health")
def health():
    return jsonify(status="ok", teams=TEAMS)


@app.post("/route")
def route_one():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="Send a JSON object, e.g. {\"request_text\": \"installer did not turn up\"}"), 400
    if not str(body.get("request_text", "")).strip():
        return jsonify(error="request_text is required (the customer's message)."), 400
    if body.get("channel") not in (None, *CHANNELS):
        return jsonify(error=f"channel must be one of {CHANNELS}"), 400
    if body.get("warranty_status") not in (None, *WARRANTY):
        return jsonify(error=f"warranty_status must be one of {WARRANTY}"), 400
    try:
        return jsonify(route(body))
    except Exception as e:  # never show a stack trace to a service-desk agent
        return jsonify(error="Could not route this request. Please route it by hand.", detail=str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
