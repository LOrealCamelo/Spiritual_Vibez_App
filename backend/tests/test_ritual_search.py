"""Exercise the actual HTTP query used by the web and native ritual finder."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.mark.parametrize("query,expected", [
    ("cinnamon", "Cinnamon & Bay Leaf Abundance Sweep"),
    ("ROSEMARY", "Fast Cash Rosemary Salt Bath"),
    ("Thursday", "Cinnamon & Bay Leaf Abundance Sweep"),
    ("reciprocal", "Rose Quartz & Honey Self-Love Bath"),
])
def test_search_covers_title_materials_timing_and_steps(query, expected):
    with TestClient(app) as client:
        response = client.get("/api/rituals/search", params={"category": "all", "query": query})
    assert response.status_code == 200
    matches = response.json()["rituals"]
    assert expected in [ritual["title"] for ritual in matches]
    assert all("tools" in ritual for ritual in matches)


def test_no_match_returns_empty_list_instead_of_server_error():
    with TestClient(app) as client:
        response = client.get("/api/rituals/search", params={"query": "not-a-real-ritual-xyz"})
    assert response.status_code == 200
    assert response.json() == {"count": 0, "rituals": []}


def test_search_handles_records_without_optional_fields(monkeypatch):
    from backend.routers import rituals
    monkeypatch.setattr(rituals, "RITUALS", [{"id": "minimal", "title": "Simple pause", "cat": "wellbeing"}])
    with TestClient(app) as client:
        response = client.get("/api/rituals/search", params={"query": "unmatched"})
    assert response.status_code == 200
    assert response.json()["count"] == 0
