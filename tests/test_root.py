"""Tests for the root endpoint (GET /)"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [307, 308]
    assert "/static/index.html" in response.headers["location"]


def test_root_follows_redirect_to_static_index(client):
    """Test that root endpoint successfully redirects to static index.html"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
