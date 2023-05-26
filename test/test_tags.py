import datetime

import sqlalchemy
from fastapi.testclient import TestClient
from src.api.server import app
import json
from src import access_ctrl
from test.test_data import data_loader
from test.testfixture import db_test_fixture
from pytest_mock import mocker

client = TestClient(app)


def test_get_tags1(db_test_fixture):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)
    tags1 = {
        0: 'Untagged'
    }
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == len(tags1)
    for x in jsondict:
        print(x)
        assert x["name"] == tags1[x["tag_id"]]


def test_get_tags2(db_test_fixture):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)
    tags1 = {
        0: 'Untagged',
        1: 'hello',
        2: 'there'
    }
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged'),
        (1, 2, 'hello'),
        (2, 2, 'there');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == len(tags1)
    for x in jsondict:
        print(x)
        assert x["name"] == tags1[x["tag_id"]]


def test_create_tag1(db_test_fixture):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)
    tags1 = ['hello']
    params = {"name": "hello"}  # Use a dictionary with the "name" key
    response = client.post("/tags/", params=params)
    assert response.status_code == 200
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == len(tags1)
    print(jsondict)
    for x in jsondict:
        print(x)
        assert x["name"] in tags1


def test_create_tag2(db_test_fixture):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)
    tags1 = ['Untagged']
    params = {"name": "Untagged"}  # Use a dictionary with the "name" key
    response = client.post("/tags/", params=params)
    assert response.status_code == 200
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == len(tags1)
    print(jsondict)
    for x in jsondict:
        print(x)
        assert x["name"] in tags1


def test_remove_tag1(db_test_fixture):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)
    params = {"name": "Untagged"}  # Use a dictionary with the "name" key
    response = client.post("/tags/", params=params)
    assert response.status_code == 200
    id = int(response.text)
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) != 0
    params = {"id": id}
    response = client.delete("/tags/", params=params)
    assert response.status_code == 200
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == 0


def test_remove_tag2(db_test_fixture):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)
    params = {"name": "whatever"}  # Use a dictionary with the "name" key
    response = client.post("/tags/", params=params)
    assert response.status_code == 200
    id = int(response.text)
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) != 0
    params = {"id": id}
    response = client.delete("/tags/", params=params)
    assert response.status_code == 200
    response = client.get("/tags/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == 0
