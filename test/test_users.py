from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import sqlalchemy as sa
from src.api.server import app
import json
import bcrypt
from src import access_ctrl

from test.testfixture import db_test_fixture
from pytest_mock import mocker

client = TestClient(app)


def test_add_user(db_test_fixture):
	engine = db_test_fixture
	
	user = {
		"username" : "saulgoodman",
		"password" : "bettercallsaul"
	}
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 200
	uid = int(response.content)
	stmt = sa.text(
		"""
		SELECT id, username, password_hash FROM users
		WHERE id = :qid
		AND username = :qusername
		"""
	)
	with engine.connect() as conn:
		result = conn.execute(stmt, { "qid" : uid, "qusername" : user["username"]})
	row = result.one()
	assert bcrypt.checkpw(user["password"].encode(), row.password_hash.encode())


def test_add_dup_user(db_test_fixture):
	engine = db_test_fixture
	
	user = {
		"username" : "saulgoodman",
		"password" : "bettercallsaul"
	}
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 200
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 422


def test_login(db_test_fixture):
	engine = db_test_fixture
	user = {
		"username" : "saulgoodman",
		"password" : "bettercallsaul"
	}
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 200

	response = client.post("/login/", content=json.dumps(user))
	assert response.status_code == 200
	key = json.loads(response.content)["token"]
	
	assert access_ctrl.check_logged_in(key)

	
def test_login_wrong_pw(db_test_fixture):
	engine = db_test_fixture
	user = {
		"username" : "saulgoodman",
		"password" : "bettercallsaul"
	}
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 200

	user["password"] = "bettercallchuck"

	response = client.post("/login/", content=json.dumps(user))
	assert response.status_code == 200
	key = json.loads(response.content)["token"]

	assert key is None
	assert not access_ctrl.check_logged_in(key)


def test_logout(db_test_fixture):
	engine = db_test_fixture
	user = {
		"username" : "saulgoodman",
		"password" : "bettercallsaul"
	}
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 200

	response = client.post("/login/", content=json.dumps(user))
	assert response.status_code == 200
	key = json.loads(response.content)["token"]
	

	response = client.post(f"/logout/?session_key={key}")
	assert response.status_code == 200

	assert not access_ctrl.check_logged_in(key)


def test_logout_timer(db_test_fixture, mocker):
	engine = db_test_fixture
	user = {
		"username" : "saulgoodman",
		"password" : "bettercallsaul"
	}
	response = client.post("/accounts/", content=json.dumps(user))
	assert response.status_code == 200

	response = client.post("/login/", content=json.dumps(user))
	assert response.status_code == 200
	key = json.loads(response.content)["token"]
	
	mocker.patch(
		'src.access_ctrl._dt_now',
		lambda : datetime.now() + timedelta(0, 0, 0, 0, 16)
	)
	# 16 minutes pass...
	
	assert not access_ctrl.check_logged_in(key)