import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_email_valid():
    pass

def test_analyze_email_too_short():
    pass

def test_analyze_url_valid():
    pass

def test_analyze_url_invalid():
    pass

def test_analyze_image_valid():
    pass

def test_analyze_image_wrong_mime():
    pass
