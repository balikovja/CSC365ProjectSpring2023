from fastapi.testclient import TestClient
from src.api.server import app
import json
import user_session

user_session.test_user()

client = TestClient(app)


def test_get_categories():
    response = client.get("/categories/")
    print (response.json())
    assert response.status_code == 200
    # complete verification that correct result was returned


def test_get_my_current_budget():
    response = client.get("/my_current_budget/")
    print (response.json())
    assert response.status_code == 200

