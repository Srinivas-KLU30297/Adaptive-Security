import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_cases():
    pass

def test_case_pagination():
    pass

def test_case_filter_verdict():
    pass

def test_get_case_detail():
    pass

def test_get_case_not_found():
    pass

def test_get_case_unauthorized():
    pass
