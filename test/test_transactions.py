import datetime

import sqlalchemy
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.api.server import app
import json
from src import access_ctrl
from test.test_data import data_loader
from test.test_data.FakeDataGenerator import FakeDataGenerator
from test.testfixture import db_test_fixture
from pytest_mock import mocker

client = TestClient(app)


class TransactionJson(BaseModel):
    category: int
    date: datetime.date
    place: str
    amount: float
    tag: int
    note: str


def test_Faker_transactions():
    generator = FakeDataGenerator()
    generator.clear_tables()
    generator.insert_user_data(10)
    generator.insert_tag_data(40)
    generator.insert_transaction_data(1000)
    assert True


def test_get_trans1(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    trans1 = {
        400: 'Vons'
    }
    stmt = sqlalchemy.text(
        """
        INSERT INTO transactions (id, user_id, place, amount, tag_id) VALUES
        (400, 2, 'Vons', 52.5, 0);
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    for x in jsondict:
        print(x)
        assert x["place"] == trans1[x["id"]]


def test_get_trans2(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    trans1 = {
        400: 52.5
    }
    stmt = sqlalchemy.text(
        """
        INSERT INTO transactions (id, user_id, place, amount, tag_id) VALUES
        (400, 2, 'Vons', 52.5, 0);
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    for x in jsondict:
        print(x)
        assert x["amount"] == trans1[x["id"]]


import json

def test_add_trans1(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    transJSON = TransactionJson(
        category=1,
        date=datetime.date(2020, 4, 20),
        place='Vons',
        amount=52.5,
        tag=0,
        note='hi'
    )
    json_data = transJSON.dict()
    json_data["date"] = transJSON.date.isoformat()  # Convert date to string representation
    response = client.post("/transactions/", json=json_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    inserted_id = int(response.text)
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    for x in jsondict:
        print(x)
        assert x["transaction_id"] == inserted_id
        assert x["place"] == transJSON.place



def test_add_trans2(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    transJSON = TransactionJson(
        category=1,
        date=datetime.date(2021, 4, 20),
        place='Safeway',
        amount=5.5,
        tag=0,
        note='hello'
    )
    json_data = transJSON.dict()
    json_data["date"] = transJSON.date.isoformat()  # Convert date to string representation
    response = client.post("/transactions/", json=json_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    inserted_id = int(response.text)
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    for x in jsondict:
        print(x)
        assert x["transaction_id"] == inserted_id
        assert x["place"] == transJSON.place


def test_remove_trans1(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    stmt = sqlalchemy.text(
        """
        INSERT INTO transactions (id, user_id, place, amount, tag_id) VALUES
        (400, 2, 'Vons', 52.5, 0);
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    params = {"id": 400}
    response = client.delete("/transactions/", params=params)
    assert response.status_code == 200


def test_remove_trans2(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    stmt = sqlalchemy.text(
        """
        INSERT INTO transactions (id, user_id, place, amount, tag_id) VALUES
        (450, 2, 'Vons', 52.5, 0);
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    params = {"id": 450}
    response = client.delete("/transactions/", params=params)
    assert response.status_code == 200


def test_update_trans1(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    transJSON = TransactionJson(
        category=1,
        date=datetime.date(2021, 4, 20),
        place='Safeway',
        amount=5.5,
        tag=0,
        note='hello'
    )
    json_data = transJSON.dict()
    json_data["date"] = transJSON.date.isoformat()  # Convert date to string representation
    response = client.post("/transactions/", json=json_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    id = int(response.text)
    params = {"place": "hope this works"}
    response = client.put(f"/transactions/{id}", params=params)
    assert response.status_code == 200
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    for x in jsondict:
        print(x)
        assert x["transaction_id"] == id
        assert x["place"] == "hope this works"


def test_update_trans2(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    transJSON = TransactionJson(
        category=1,
        date=datetime.date(2021, 4, 20),
        place='Safeway',
        amount=5.5,
        tag=0,
        note='hello'
    )
    json_data = transJSON.dict()
    json_data["date"] = transJSON.date.isoformat()  # Convert date to string representation
    response = client.post("/transactions/", json=json_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    id = int(response.text)
    params = {"note": "hope this works"}
    response = client.put(f"/transactions/{id}", params=params)
    assert response.status_code == 200
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    for x in jsondict:
        print(x)
        assert x["transaction_id"] == id
        assert x["note"] == "hope this works"


def test_split_trans1(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    transJSON = TransactionJson(
        category=1,
        date=datetime.date(2021, 4, 20),
        place='Safeway',
        amount=5,
        tag=0,
        note='hello'
    )
    json_data = transJSON.dict()
    json_data["date"] = transJSON.date.isoformat()  # Convert date to string representation
    response = client.post("/transactions/", json=json_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    id = int(response.text)
    params = {
              "transaction1_amount": 4,
              "transaction1_category": 1,
              "transaction2_amount": 1,
              "transaction2_category": 1
              }
    response = client.put(f"/transactions/{id}/split", params=params)
    print(response.json())
    assert response.status_code == 200
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == 2


def test_split_trans2(db_test_fixture):
    engine = db_test_fixture
    stmt = sqlalchemy.text(
        """
        INSERT INTO tags (id, user_id, name) VALUES
        (0, 2, 'Untagged');
        """
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    transJSON = TransactionJson(
        category=1,
        date=datetime.date(2021, 4, 20),
        place='Safeway',
        amount=19,
        tag=0,
        note='hello'
    )
    json_data = transJSON.dict()
    json_data["date"] = transJSON.date.isoformat()  # Convert date to string representation
    response = client.post("/transactions/", json=json_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    id = int(response.text)
    params = {
        "transaction1_amount": 4,
        "transaction1_category": 1,
        "transaction2_amount": 15,
        "transaction2_category": 1
    }
    response = client.put(f"/transactions/{id}/split", params=params)
    print(response.json())
    assert response.status_code == 200
    response = client.get("/transactions/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == 2
