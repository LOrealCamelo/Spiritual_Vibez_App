"""HTTP smoke tests for the Spiritual Vibez FastAPI application.

These tests verify routing and response shapes, unlike the legacy script
which invokes Python functions directly.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_tarot_catalog():
    response = client.get("/api/tarot/cards")
    assert response.status_code == 200
    assert response.json()["count"] == 78

def test_spread_catalog():
    response = client.get("/api/tarot/spreads")
    assert response.status_code == 200
    assert response.json()["count"] == 48

def test_daily_transits():
    response = client.get("/api/astrology/daily-transits", params={"sign": "Libra", "date": "2026-11-05"})
    assert response.status_code == 200
    assert response.json()["selected_sign"] == "Libra"

def test_numerology_lessons():
    response = client.get("/api/synastry/numerology-lessons")
    assert response.status_code == 200
    assert len(response.json()["lessons"]) == 12

def test_sample_tarot_draw():
    response = client.post("/api/tarot/spreads/deal-slot", json={"spread_id":"reset-energy","slot_num":1,"exclude_card_ids":[]})
    assert response.status_code == 200
    assert "card" in response.json()
