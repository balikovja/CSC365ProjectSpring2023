import sqlalchemy
from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from src import user_session
from fastapi.params import Query

router = APIRouter()


@router.get("/categories/", tags=["info", "budgets"])
def get_categories():
    """
    This endpoint returns a list of all budget categories. For each category it returns:
    * `id`: The category's internal id
    * `name`: The name. ("Rent", "Entertainment", etc)
    """
    # insert code to make this work
    sql = sqlalchemy.select(
        db.categories.c.id,
        db.categories.c.name
    ).order_by(db.categories.c.name)

    with db.engine.connect() as conn:
        result = conn.execute(sql)
        json = (
            {
                "id" : row.id,
                "name" : row.name,
            }
            for row in result
        )

        return json


@router.get("/my_current_budget/", tags=["budget"])
def get_my_current_budget():
    """
    This endpoint returns your configured budgeting categories. For each category it returns:
    * `category_name`: The name of the category.
    * `allotment`: This category's budget allotment.
    * `spent`: How much of the allotment has already been spent.
    * `start_date`: The start date of the curent period for this category.
    * `end_date`: The end date of the curent period for this category.
    * `period`: The period defined for this budget (Weekly, Quarterly, etc.)
    """

    with open("src/api/queries/my_current_budget.sql") as file:
        sql = sqlalchemy.text(file.read())
    
    with db.engine.connect() as conn:
        result = conn.execute(sql, {"quserid" : user_session.user_id()})
        json = (
            {
                "category_name" : row.name,
                "allotment" : row.budget_amount,
                "spent" : row.category_spent,
                "start_date" : row.start_date,
                "end_date" : row.end_date,
                "period" : row.period_text
            }
            for row in result
        )
        return json
    
    # insert code to make this work

# THIS IS HERE AS AN EXAMPLE, DELETE WHEN NOT NEEDED ANYMORE
# @router.get("/movies/{movie_id}", tags=["movies"])
# def get_movie(movie_id: int):
#     """
#     This endpoint returns a single movie by its identifier. For each movie it returns:
#     * `movie_id`: the internal id of the movie.
#     * `title`: The title of the movie.
#     * `top_characters`: A list of characters that are in the movie. The characters
#       are ordered by the number of lines they have in the movie. The top five
#       characters are listed.
#
#     Each character is represented by a dictionary with the following keys:
#     * `character_id`: the internal id of the character.
#     * `character`: The name of the character.
#     * `num_lines`: The number of lines the character has in the movie.
#
#     """
#     # Get the movie they asked for with its title and id
#     stmt = (
#         sqlalchemy.select(
#             db.movies.c.movie_id,
#             db.movies.c.title,
#         )
#             .where(db.movies.c.movie_id == movie_id)
#     )
#
#     stmt2 = (
#         sqlalchemy.select(
#             db.characters.c.character_id,
#             db.characters.c.name,
#             sqlalchemy.func.count(db.lines.c.line_id).label("line_count")
#         )
#             .join(db.lines, db.lines.c.character_id == db.characters.c.character_id)
#             .join(db.movies, db.movies.c.movie_id == db.characters.c.movie_id)
#             .where(db.movies.c.movie_id == movie_id)
#             .group_by(db.characters.c.character_id)
#             .order_by(sqlalchemy.desc("line_count"))
#     )
#
#     with db.engine.connect() as conn:
#         result = conn.execute(stmt)
#         result2 = conn.execute(stmt2)
#         charJSON = []
#         json = []
#         if result.rowcount == 0:
#             raise HTTPException(status_code=404, detail="movie not found.")
#         for row in result2:
#             charJSON.append(
#                 {
#                     "character_id": row.character_id,
#                     "character": row.name,
#                     "num_lines": row.line_count,
#                 }
#             )
#         for row in result:
#             json = {
#                     "movie_id": row.movie_id,
#                     "title": row.title,
#                     "top_characters": charJSON[:5]
#                    }
#     return json
