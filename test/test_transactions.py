from fastapi.testclient import TestClient
from src.api.server import app
import json
from src import user_session

user_session.test_user()

client = TestClient(app)


def test_get_trans1():
    response = client.get("/transactions/")
    print(response.json())
    assert response.status_code == 200
    # complete verification that correct result was returned


def test_get_trans2():
    response = client.get("/transactions/")
    print(response.json())
    assert response.status_code == 200
    # complete verification that correct result was returned


def test_add_trans1():
    response = client.post("/transactions/")
    print(response.json())
    assert response.status_code == 200


def test_add_trans2():
    response = client.post("/transactions/")
    print(response.json())
    assert response.status_code == 200


def test_remove_trans1():
    response = client.delete("/transactions/")
    print(response.json())
    assert response.status_code == 200


def test_remove_trans2():
    response = client.delete("/transactions/")
    print(response.json())
    assert response.status_code == 200


def test_update_trans1():
    response = client.put("/transactions/{id}")
    print(response.json())
    assert response.status_code == 200


def test_update_trans2():
    response = client.put("/transactions/{id}")
    print(response.json())
    assert response.status_code == 200


def test_split_trans1():
    response = client.put("/transactions/{id}/split")
    print(response.json())
    assert response.status_code == 200


def test_split_trans2():
    response = client.put("/transactions/{id}/split")
    print(response.json())
    assert response.status_code == 200
