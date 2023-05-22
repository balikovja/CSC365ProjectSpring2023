import sqlalchemy
from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from src import user_session
from fastapi.params import Query
from pydantic import BaseModel
from typing import Dict
import datetime

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


@router.get("/{user_id}/current_budget/", tags=["budget"])
def get_my_current_budget(user_id: int):
    """
    This endpoint returns your configured budgeting categories. For each category it returns:
    * `category_name`: The name of the category.
    * `allotment`: This category's budget allotment.
    * `spent`: How much of the allotment has already been spent.
    * `start_date`: The start date of the curent period for this category.
    * `end_date`: The end date of the curent period for this category.
    * `period`: The period defined for this budget (Weekly, Quarterly, etc.)
    """

    if not user_session.check_logged_in(user_id):
        raise HTTPException(403, "Not logged in")

    with open("src/api/queries/my_current_budget.sql") as file:
        sql = sqlalchemy.text(file.read())

    current_date = datetime.datetime.today().strftime("%Y-%m-%d")
    
    with db.engine.connect() as conn:
        result = conn.execute(sql, {"quserid" : user_id, "qcurrent_date" : current_date})
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
    start_date: str
    end_date: str
    amount: str
    period_id: int


class AllBudgetsDefJson(BaseModel):
    categories: Dict[int, BudgetDefJson]

@router.post("/{user_id}/budgets/", tags=["budget"])
def post_define_budgets(user_id: int, budgetdef: AllBudgetsDefJson):
    """
    This endpoint adds budget instances for each specified category.
    * `start_date`: The start of this budget period.
    * `end_date`: The end of this budget period.
    * `amount`: How much money.
    * `period_id`: The period id defined for this budget (1: Weekly, 4: Quarterly, etc.)
    """
    if not user_session.check_logged_in(user_id):
        raise HTTPException(403, "Not logged in")

    # Validate category selections
    categories = list(get_categories())
    for cat_id in budgetdef.categories.keys():
        if cat_id not in (cat["id"] for cat in categories):
            raise HTTPException(status_code=400, detail=f"invalid category {cat_id} (use get_categories)")

    rows_list = [
        {
            "user_id" : user_session.user_id(),
            "budget_amount" : spec.amount,
            "category_id" : cat,
            "start_date" : spec.start_date,
            "end_date" : spec.end_date,
            "period_type_id" : spec.period_id
        }
        for cat, spec in budgetdef.categories.items()
    ]

    stmt = (
        sqlalchemy.insert(db.budgets)
        .values(rows_list)
        .returning(db.budgets.c.id)
    )
    
    with db.engine.begin() as conn:
        result = conn.execute(stmt)
        json = (
            {
                "budget_id" : row.id
            }
            for row in result
        )
        return json

