from fastapi.testclient import TestClient
from src.api.server import app
import json
from src import user_session

user_session.test_user()

client = TestClient(app)


def test_get_tags1():
    response = client.get("/tags/")
    print(response.json())
    assert response.status_code == 200
    # complete verification that correct result was returned


def test_get_tags2():
    response = client.get("/tags/")
    print(response.json())
    assert response.status_code == 200
    # complete verification that correct result was returned


def test_create_tag1():
    response = client.post("/tags/")
    print (response.json())
    assert response.status_code == 200


def test_create_tag2():
    response = client.post("/tags/")
    print (response.json())
    assert response.status_code == 200


def test_remove_tag1():
    response = client.delete("/tags/")
    print (response.json())
    assert response.status_code == 200


def test_remove_tag2():
    response = client.delete("/tags/")
    print (response.json())
    assert response.status_code == 200
