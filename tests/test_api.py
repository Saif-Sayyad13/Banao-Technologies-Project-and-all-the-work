import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from kestrel.text import clean, TEAMS

c = app.test_client()

def post(b): return c.post("/route", json=b)

def test_health():
    assert c.get("/health").get_json()["status"] == "ok"

def test_routes_install_even_if_customer_says_paid():
    j = post({"request_text": "i paid extra for installation of my water purifier, when will the technician come", "channel": "chat",
              "warranty_status": "in_warranty", "product_family": "Water Purifier"}).get_json()
    assert j["team"] == "Installs & Demo" and not j["needs_triage"]

def test_vague_goes_to_triage():
    j = post({"request_text": "please call me about my purifier"}).get_json()
    assert j["needs_triage"] and j["team"] in TEAMS

def test_bad_input_is_polite():
    assert post({}).status_code == 400
    assert c.post("/route", data="not json").status_code == 400
    assert post({"request_text": "x", "channel": "fax"}).status_code == 400

def test_mojibake_and_ids():
    assert clean("urgÃ©nt: installer did not turn up for room heater order KO2608878") == "urgent installer did not turn up for room heater order"
    assert clean("claim status â€¦ SR75294") == "claim status"
