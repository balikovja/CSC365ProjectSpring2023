import os
import sqlalchemy
import dotenv


def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())

# Create a metadata object for each table
metadata_obj = sqlalchemy.MetaData()

users = sqlalchemy.Table("users", metadata_obj, autoload_with=engine)
transactions = sqlalchemy.Table("transactions", metadata_obj, autoload_with=engine)
budgets = sqlalchemy.Table("budgets", metadata_obj, autoload_with=engine)
tags = sqlalchemy.Table("tags", metadata_obj, autoload_with=engine)
categories = sqlalchemy.Table("categories", metadata_obj, autoload_with=engine)
period_types = sqlalchemy.Table("period_types", metadata_obj, autoload_with=engine)

print(metadata_obj)
