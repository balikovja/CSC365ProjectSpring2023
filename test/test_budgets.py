from fastapi.testclient import TestClient
from src.api.server import app
import json

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

# EXAMPLES, DELETE WHEN NO LONGER NEEDED
# def test_get_movie():
#     response = client.get("/movies/44")
#     assert response.status_code == 200
#
#     with open("test/movies/44.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)
#
#
# def test_movies():
#     response = client.get("/movies/")
#     assert response.status_code == 200
#
#     with open("test/movies/root.json", encoding="utf-8") as f:
#         assert response.json() == json.load(f)
#
# def test_sort_filter():
#     response = client.get("/movies/?name=big&limit=50&offset=0&sort=rating")
#     assert response.status_code == 200
#
#     with open(
#         "test/movies/movies-name=big&limit=50&offset=0&sort=rating.json",
#         encoding="utf-8",
#     ) as f:
#         assert response.json() == json.load(f)
#
# def test_404():
#     response = client.get("/movies/1")
#     assert response.status_code == 404
