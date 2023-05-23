import datetime
from fastapi.testclient import TestClient
from src.api.server import app
import json
from src import user_session

from test.testfixture import db_test_fixture
from pytest_mock import mocker

from test.test_data import data_loader

client = TestClient(app)

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

categories_back = {
    'Rent': 1,
    'Groceries': 2,
    'Restaraunts': 3,
    'Entertainment': 4,
    'Clothing': 5,
    'Electronics': 6, 
    'Home Goods': 7, 
    'Medical': 8
}

def test_get_categories(db_test_fixture):
    engine = db_test_fixture
    
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

    budget_vals = {
        1: 100.00,
        2: 200.00,
        3: 300.00,
        4: 400.00,
        5: 500.00,
        6: 600.00,
        7: 700.00, 
        8: 800.00
    }
    # calculated with excel based on the test data
    budget_spend = {
        1: None,
        2: 346.82,
        3: 99.17,
        4: 633.10,
        5: 132.20,
        6: None,
        7: None, 
        8: 35.98
    }

    budget_start = {
        1: "2023-01-01",
        2: "2023-01-01",
        3: "2023-01-03",
        4: "2022-04-01",
        5: "2023-01-01",
        6: "2023-01-01",
        7: "2023-01-01",
        8: "2022-12-25",
    }
    budget_end = {
        1: "2023-01-31",
        2: "2023-12-31",
        3: "2023-02-02",
        4: "2023-03-31",
        5: "2023-03-31",
        6: "2023-01-14",
        7: "2023-01-07",
        8: "2023-01-24",
    }
    budget_period = {
        1: "Monthly",
        2: "Annual",
        3: "Monthly",
        4: "Annual",
        5: "Quarterly",
        6: "Biweekly",
        7: "Weekly",
        8: "Monthly",
    }

    mocker.patch(
        'src.api.budget.datetime_today',
        lambda : datetime.date(2023,1,5)
    )
    response = client.get("/1/current_budget/")
    assert response.status_code == 200
    j = response.json()
    for x in j:
        cat_id = categories_back[x["category_name"]]
        assert x["allotment"] == budget_vals[cat_id], cat_id
        assert x["spent"] == budget_spend[cat_id], cat_id
        assert x["start_date"] == budget_start[cat_id], cat_id
        assert x["end_date"] == budget_end[cat_id], cat_id
        assert x["period"] == budget_period[cat_id], cat_id

    
def test_get_my_current_budget2(db_test_fixture, mocker):
    engine = db_test_fixture
    data_loader.load_transactions(engine)
    data_loader.load_budgets(engine)

    budget_vals = {
        1: 100.00,
        2: 200.00,
        3: 300.00,
        4: 400.00,
        5: 500.00,
        6: 600.00,
        7: 700.00, 
        8: 800.00
    }
    # calculated with excel based on the test data
    budget_spend = {
        1: None,
        2: 346.82,
        3: 99.17,
        4: 633.10,
        5: 132.20,
        6: None,
        7: 56.89, 
        8: 35.98
    }

    budget_start = {
        1: "2023-01-01",
        2: "2023-01-01",
        3: "2023-01-03",
        4: "2022-04-01",
        5: "2023-01-01",
        6: "2023-01-01",
        7: "2023-01-08",
        8: "2022-12-25",
    }
    budget_end = {
        1: "2023-01-31",
        2: "2023-12-31",
        3: "2023-02-02",
        4: "2023-03-31",
        5: "2023-03-31",
        6: "2023-01-14",
        7: "2023-01-14",
        8: "2023-01-24",
    }
    budget_period = {
        1: "Monthly",
        2: "Annual",
        3: "Monthly",
        4: "Annual",
        5: "Quarterly",
        6: "Biweekly",
        7: "Weekly",
        8: "Monthly",
    }

    mocker.patch(
        'src.api.budget.datetime_today',
        lambda : datetime.date(2023,1,9)
    )
    response = client.get("/1/current_budget/")
    assert response.status_code == 200
    j = response.json()
    for x in j:
        cat_id = categories_back[x["category_name"]]
        assert x["allotment"] == budget_vals[cat_id], cat_id
        assert x["spent"] == budget_spend[cat_id], cat_id
        assert x["start_date"] == budget_start[cat_id], cat_id
        assert x["end_date"] == budget_end[cat_id], cat_id
        assert x["period"] == budget_period[cat_id], cat_id

def test_get_budget(db_test_fixture):
    engine = db_test_fixture
    expect =  [
    {"category": categories[1],
     "start_date": "2023-01-01",
     "end_date": "2023-01-31",
     "amount": 100,
     "period": "Monthly"},
    {"category": categories[2],
     "start_date": "2023-01-01",
     "end_date": "2023-12-31",
     "amount": 200,
     "period": "Annual"},
    {"category": categories[3],
     "start_date": "2023-01-03",
     "end_date": "2023-02-02",
     "amount": 300,
     "period": "Monthly"},
    {"category": categories[4],
     "start_date": "2022-04-01",
     "end_date": "2023-03-31",
     "amount": 400,
     "period": "Annual"},
    {"category": categories[5],
     "start_date": "2023-01-01",
     "end_date": "2023-03-31",
     "amount": 500,
     "period": "Quarterly"},
    {"category": categories[6],
     "start_date": "2023-01-01",
     "end_date": "2023-01-14",
     "amount": 600,
     "period": "Biweekly"},
    {"category": categories[7],
     "start_date": "2023-01-01",
     "end_date": "2023-01-07",
     "amount": 700,
     "period": "Weekly"},
    {"category": categories[8],
     "start_date": "2022-12-25",
     "end_date": "2023-01-24",
     "amount": 800,
     "period": "Monthly"},
    {"category": categories[7],
     "start_date": "2023-01-08",
     "end_date": "2023-01-14",
     "amount": 700,
     "period": "Weekly"}
    ]
    expect.sort(key=lambda x: (x["start_date"], x["amount"]))
    data_loader.load_budgets(engine)
    response = client.get("/1/budgets/")
    assert response.status_code == 200
    j = response.json()
    for x in j:
        del x["budget_id"] # ignoring id
    assert j == expect
