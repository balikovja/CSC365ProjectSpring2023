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
metadata_obj1 = sqlalchemy.MetaData()
movies = sqlalchemy.Table("movies", metadata_obj1, autoload_with=engine)

metadata_obj2 = sqlalchemy.MetaData()
characters = sqlalchemy.Table("characters", metadata_obj2, autoload_with=engine)

metadata_obj3 = sqlalchemy.MetaData()
conversations = sqlalchemy.Table("conversations", metadata_obj3, autoload_with=engine)

metadata_obj4 = sqlalchemy.MetaData()
lines = sqlalchemy.Table("lines", metadata_obj4, autoload_with=engine)

# The sql we want to execute
sql = """
SELECT year, AVG(imdb_rating) AS avg_movie_ratings
FROM movies
GROUP BY year
ORDER BY avg_movie_ratings DESC
"""

# Create a single connection to the database. Later we will discuss pooling connections.
with engine.connect() as conn:
    # Run the sql and returns a CursorResult object which represents the SQL results
    result = conn.execute(sqlalchemy.text(sql))
    # Iterate over the CursorResult object row by row and just print.
    # In a real application you would access the fields directly.
    for row in result:
        print(row)
