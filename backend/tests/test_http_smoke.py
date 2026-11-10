"""HTTP smoke tests for the Spiritual Vibz FastAPI application.

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

def test_web_app_has_new_branding():
    response = client.get("/")
    assert response.status_code == 200
    assert "Spiritual Vibz" in response.text
    assert "AuraMystic" not in response.text

def test_new_css_js_and_illustration_are_served():
    stylesheet = client.get("/styles.css")
    script = client.get("/app.js")
    illustration = client.get("/guide.svg")
    assert stylesheet.status_code == 200 and "feature-grid" in stylesheet.text
    assert script.status_code == 200 and "Spiritual Vibz" in script.text
    assert illustration.status_code == 200 and illustration.headers["content-type"].startswith("image/svg+xml")


def test_approved_illustrations():
    for name in ["cartoon_me_transparent3.png", "ui_background.png", "illustrations/cosmic.png", "illustrations/study.png", "illustrations/journal.png", "illustrations/ritual.png", "me_reset_your_energy.png"]:
        response=client.get("/assets/"+name)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/png")
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    artwork=client.get("/artwork.js")
    assert artwork.status_code == 200 and "CARD_PANELS" in artwork.text
    assert client.get("/assets/home_shuffle_spread.png").status_code == 404
    appjs=client.get("/app.js")
    assert appjs.status_code == 200 and "Spiritual Vibz" in appjs.text
