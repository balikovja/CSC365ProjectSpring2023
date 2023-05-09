import datetime
from enum import Enum

from fastapi import APIRouter
from pydantic import BaseModel
import src.database as db

router = APIRouter()


class TransactionJson(BaseModel):
    category: str
    date: datetime.date
    place: str
    amount: float
    tag: str
    note: str


@router.post("/add_transaction/", tags=["budgets"])
def add_transaction(transaction: TransactionJson):
    """
    This endpoint adds a transaction to the current user (currently hardcoded
    to user.id = 2 as logins are not implemented). The transaction is represented
    by the category_id, the transaction_date, the place it occurred, the amount,
    the tag, and a note.

    The endpoint ensures that a valid category was chosen

    The endpoint returns the id of the resulting transaction that was created
    """
    # insert code to make this work


@router.delete("/remove_transaction/", tags=["budgets"])
def remove_transaction(id: int):
    """
    This endpoint removes the transaction with the given transaction id for the
    current user (currently hardcoded to user.id = 2 as logins are not implemented)

    """
    # insert code to make this work


class transaction_sort_options(str, Enum):
    dateNewToOld = "dateNewToOld"
    dateOldToNew = "dateOldToNew"
    priceLowToHigh = "priceLowToHigh"
    priceHighToLow = "priceHighToLow"
    category = "category"
    place = "place"


@router.get("/transactions/", tags=["budgets"])
def transactions(
        id: int = 0,
        category: str = "",
        place: str = "",
        start_date: datetime.date = datetime.date(1, 1, 1),
        end_date: datetime.date = datetime.date.today(),
        min_price: float = 0,
        max_price: float = 10000000,
        sort: transaction_sort_options = transaction_sort_options.dateNewToOld,
):
    """
    This endpoint returns your budgets categories. For each category it returns:
    * `category_name`: The name of the category.
    * `budget`: This category's budget allotment.
    * `spent`: How much of the allotment has already been spent.

    """
    # insert code to make this work
