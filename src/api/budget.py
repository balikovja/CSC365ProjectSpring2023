import sqlalchemy
from fastapi import APIRouter, HTTPException
from enum import Enum

from sqlalchemy.sql.operators import as_
from src import access_ctrl, database as db
from fastapi.params import Query
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

router = APIRouter()


@router.get("/categories/", tags=["budget"])
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

# Wrapper to allow mocking
def datetime_today():
    return datetime.today()

@router.get("/current_budget/", tags=["budget"])
def get_my_current_budget(session_key: str):
    """
    This endpoint returns your configured budgeting categories. For each category it returns:
    * `category_name`: The name of the category.
    * `allotment`: This category's budget allotment.
    * `spent`: How much of the allotment has already been spent.
    * `start_date`: The start date of the curent period for this category.
    * `end_date`: The end date of the curent period for this category.
    * `period`: The period defined for this budget (Weekly, Quarterly, etc.)
    """

    user_id = access_ctrl.check_logged_in(session_key)
    if user_id is None:
        raise HTTPException(401, "Not logged in")

    with open("src/api/queries/my_current_budget.sql") as file:
        sql = sqlalchemy.text(file.read())

    current_date = datetime_today().strftime("%Y-%m-%d")
    
    with db.engine.connect() as conn:
        result = conn.execute(sql, {"quser_id" : user_id, "qcurrent_date" : current_date})
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


# TODO: Fix types
class BudgetDefJson(BaseModel):
    category_id: int
    start_date: str
    end_date: str
    amount: str
    period_id: int


class AllBudgetsDefJson(BaseModel):
    categories: List[BudgetDefJson] #fastapi/issues/5470
# 
@router.post("/budgets/", tags=["budget"])
def post_define_budgets(session_key: str, budgetdef: AllBudgetsDefJson):
    """
    This endpoint adds budget instances for each specified category.
    The data should be a list where each category specification has the following atributes: 
    * `category_id`: the category
    * `start_date`: The start of this budget period.
    * `end_date`: The end of this budget period.
    * `amount`: How much money.
    * `period_id`: The period id defined for this budget:
        1: Weekly, 2: Biweekly, 3: Monthly
        4: Quarterly, 5: Annual
    """

    user_id = access_ctrl.check_logged_in(session_key)
    if user_id is None:
        raise HTTPException(401, "Not logged in")

    # TODO: perhaps remove this, substitute for better error handling in the execution
    # Validate category selections
    categories = list(get_categories())
    for c in budgetdef.categories:
        cat_id = c.category_id
        if cat_id not in (cat["id"] for cat in categories):
            raise HTTPException(status_code=400, detail=f"invalid category (use get_categories)")

    rows_list = [
        {
            "user_id" : user_id,
            "budget_amount" : cat.amount,
            "category_id" : cat.category_id,
            "start_date" : cat.start_date,
            "end_date" : cat.end_date,
            "period_type_id" : cat.period_id
        }
        for cat in budgetdef.categories
    ]
    try:
        stmt = (
            sqlalchemy.insert(db.budgets)
            .values(rows_list)
            .returning(db.budgets.c.category_id, db.budgets.c.id)
        )
    except Exception as e:
        raise HTTPException(400, detail=e)
    
    with db.engine.begin() as conn:
        result = conn.execute(stmt)
        json = (
            {
                "category_name" : row.category_id,
                "budget_id" : row.id
            }
            for row in result
        )
        return json

@router.get("/budgets/", tags=["budget"])
def get_budgets(session_key: str, category: str = None):
    """
    This endpoint returns a list of all budgets for the current user
    Optionally filtered by category
    * `budget_id`: Internal budget id
    * `category`: The category associated with this budget
    * `start_date`: The start of this budget period.
    * `end_date`: The end of this budget period.
    * `amount`: How much money.
    * `period`: The period defined for this budget (Weekly, Quarterly, etc.)
    """

    user_id = access_ctrl.check_logged_in(session_key)
    if user_id is None:
        raise HTTPException(401, "Not logged in")

    # TODO: pagination

    stmt = (sqlalchemy.select(
        db.budgets.c.id,
        db.categories.c.name.label("categoryname"),
        db.budgets.c.start_date,
        db.budgets.c.end_date,
        db.budgets.c.budget_amount,
        db.period_types.c.name.label("period")
        )
    .join(db.categories, db.categories.c.id == db.budgets.c.category_id)
    .join(db.period_types, db.period_types.c.id == db.budgets.c.period_type_id)
    .where(db.budgets.c.user_id == user_id)
    .order_by(db.budgets.c.start_date, db.budgets.c.budget_amount)
    )
    if category:
        stmt = stmt.where(db.categories.c.name.lower() == category.lower())
    
    with db.engine.begin() as conn:
        result = conn.execute(stmt)
        json = (
            {
                "budget_id" : row.id,
                "category" : row.categoryname,
                "start_date" : row.start_date,
                "end_date" : row.end_date,
                "amount" : row.budget_amount,
                "period" : row.period
            }
            for row in result
        )
        return json

@router.post("/budgets/copy_budgets/", tags=["budget"])
def post_copy_budgets(session_key: str, clone_all: bool = False, multiplier: float = 1.0):
    """
    This endpoint copies the user's most recent budget for each category
    based on their specified periods. The new start dates are set as the
    day after the previous budget ends.
    * `session_key`: the session token for the user
    * `clone_all`: whether to include budgets that will be inactive on today's date
    * `multiplier`: multiply the amounts by this number for the new budgets (e.g. to account for inflation)
    Returns:
    * `ids`: a list of ids of the new budget entries
    * `message`: status message with number of new budgets
    """
    user_id = access_ctrl.check_logged_in(session_key)
    if user_id is None:
        raise HTTPException(401, "Not logged in")

    with open("src/api/queries/copy_budgets.sql") as file:
        sql = sqlalchemy.text(file.read())

    current_date = datetime_today().strftime("%Y-%m-%d")
    
    try:
        with db.engine.begin() as conn:
            result = conn.execute(sql,
                {"quser_id" : user_id,
                "qcurrent_date" : current_date,
                "qmultiplier": multiplier,
                "qcopy_override" : clone_all}
            )
            json = {
                "ids" : (r.id for r in result),
                "message" : f"Created {result.rowcount} new budgets"
            }
            return json
    except Exception as e:
        raise HTTPException(422, str(e))



