import sqlalchemy as sa

import pytest
import dotenv
import os

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_ADMIN_USER")
    DB_PASSWD = os.environ.get("POSTGRES_ADMIN_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


def prepare_db(conn):
	users_stmt = sa.text(
		"""
		INSERT INTO users (id, username)
		VALUES (1, 'test_user');
		"""
	)
	conn.execute(users_stmt)


def cleanup_db(conn):
	stmt = sa.text(
		"""
		DELETE FROM transactions;
		DELETE FROM budgets;
		DELETE FROM users;

		"""
	)
	conn.execute(stmt)
	pass

@pytest.fixture
def db_test_fixture():
	engine = sa.create_engine(database_connection_url())
	with engine.begin() as conn:
		cleanup_db(conn)
		prepare_db(conn)
	yield
