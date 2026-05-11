"""Testy FastAPI endpointow (TestClient)."""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from backend.config import settings


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    monkeypatch.setattr(settings, "database_path", path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def client():
    # Import po monkeypatch, zeby lifespan widzial nowy db path
    from backend.main import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_matches_empty(client):
    r = client.get("/api/matches")
    assert r.status_code == 200
    assert r.json() == []


def test_match_not_found(client):
    r = client.get("/api/matches/nonexistent")
    assert r.status_code == 404


def test_html_root_empty_db(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "ProbWin AI" in r.text
    assert "refresh_daily" in r.text
