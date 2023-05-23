import datetime
from fastapi.testclient import TestClient
from src.api.server import app
import json
from src import user_session

from test.testfixture import db_test_fixture
from pytest_mock import mocker

from test.test_data import data_loader

client = TestClient(app)



def test_get_categories(db_test_fixture):
    engine = db_test_fixture
    categories = {
        1: 'Rent',
        2: 'Groceries',
        3: 'Restaraunts',
        4: 'Entertainment',
        5: 'Clothing',
        6: 'Electronics', 
        7: 'Home Goods', 
        8: 'Medical'
    }
    response = client.get("/categories/")
    assert response.status_code == 200
    jsondict = response.json()
    assert len(jsondict) == len(categories)
    for x in jsondict:
        assert x["name"] == categories[x["id"]]


def test_get_my_current_budget(db_test_fixture, mocker):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)

    mocker.patch(
        'src.api.budget.datetime_today',
        lambda : datetime.date(2023,1,5)
    )
    response = client.get("/1/current_budget/")
    print (response.json())
    assert response.status_code == 200

