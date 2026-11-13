from fastapi.testclient import TestClient

from exoplanet_app.main import app

client = TestClient(app)


def test_home_page_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Exoplanet Explorer" in response.text


def test_api_stats_returns_json():
    response = client.get("/api/stats")
    assert response.status_code == 200
    payload = response.json()
    assert "total_planets" in payload
    assert "total_hosts" in payload


def test_explorer_page_renders():
    response = client.get("/explorer")
    assert response.status_code == 200
    assert "Planet Explorer" in response.text


def test_planet_detail_page_for_seed_data():
    response = client.get("/planet/1")
    assert response.status_code == 200
    assert "TRAPPIST-1 b" in response.text
