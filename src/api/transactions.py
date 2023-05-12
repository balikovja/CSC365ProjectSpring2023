import datetime
from enum import Enum
import pytz
import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import src.database as db

router = APIRouter()

#
class TransactionJson(BaseModel):
    category: str
    date: datetime.date
    place: str
    amount: float
    tag: str
    note: str


@router.post("/add_transaction/", tags=["budgets"])
def add_transaction(includeTag: bool, transaction: TransactionJson):
    """
    This endpoint adds a transaction to the current user (currently hardcoded
    to user.id = 2 as logins are not implemented). The transaction is represented
    by the category_id, the transaction_date, the place it occurred, the amount,
    the tag, and a note.

    The endpoint ensures that a valid category was chosen

    If includeTag is true, ensures that a valid tag was chosen
    If includeTag is false, does not add a tag

    The endpoint returns the id of the resulting transaction that was created
    """
    # Set your timezone
    tz = pytz.timezone('America/Los_Angeles')

    # Get the current time in your timezone
    current_time = datetime.datetime.now(tz)

    # Convert the datetime to ISO 8601 format
    iso_time = current_time.isoformat()

    with db.engine.begin() as conn:
        stmt = sqlalchemy.select(db.categories.c.id).where(db.categories.c.name == transaction.category)
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=400, detail="invalid category (use get_categories)")
        else:
            row = result.fetchone()
            categoryID = row[0]
        if includeTag:
            stmt = sqlalchemy.select(db.tags.c.id).where(db.tags.c.name == transaction.tag)
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail="invalid tag (use get_tags or create_tag)")
            else:
                row = result.fetchone()
                tagID = row[0]
        else:
            tagID = None
        # Insert transaction into transactions table
        transaction_values = {"created_at": iso_time,
                              "user_id": 2,
                              "category_id": categoryID,
                              "transaction_date": transaction.date,
                              "place": transaction.place,
                              "amount": transaction.amount,
                              "tag_id": tagID,
                              "note": transaction.note}
        transaction_stmt = db.transactions.insert().values(transaction_values).returning(db.transactions.c.id)
        transaction_result = conn.execute(transaction_stmt)
        inserted_id = transaction_result.fetchone()[0]
    return inserted_id


@router.delete("/remove_transaction/", tags=["budgets"])
def remove_transaction(id: int):
    """
    This endpoint removes the transaction with the given transaction id for the
    current user (currently hardcoded to user.id = 2 as logins are not implemented)
    """
    stmt = sqlalchemy.delete(db.transactions).where(db.transactions.c.id == id)
    stmt = stmt.where(db.transactions.c.user_id == 2)  # hardcoded to 2 currently because no login
    with db.engine.begin() as conn:
        conn.execute(stmt)


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
    # First configure sort
    if sort is transaction_sort_options.dateNewToOld:
        order_by = sqlalchemy.desc(db.transactions.c.transaction_date)
    elif sort is transaction_sort_options.dateOldToNew:
        order_by = sqlalchemy.asc(db.transactions.c.transaction_date)
    elif sort is transaction_sort_options.place:
        order_by = db.transactions.c.place
    elif sort is transaction_sort_options.category:
        order_by = db.transactions.c.category
    elif sort is transaction_sort_options.priceHighToLow:
        order_by = sqlalchemy.desc(db.transactions.c.amount)
    elif sort is transaction_sort_options.priceLowToHigh:
        order_by = sqlalchemy.asc(db.transactions.c.amount)
    else:
        assert False

    # Get all necessary fields with the proper limit, offset, and sort
    stmt = (
        sqlalchemy.select(
            db.transactions.c.id,
            db.transactions.c.created_at,
            db.transactions.c.user_id,
            db.categories.c.name.label('category_name'),
            db.transactions.c.transaction_date,
            db.transactions.c.place,
            db.transactions.c.amount,
            db.tags.c.name.label('tag_name'),
            db.transactions.c.note,
        )
            .join(db.categories, db.categories.c.id == db.transactions.c.category_id)
            .join(db.tags, db.tags.c.id == db.transactions.c.tag_id)
            .group_by(db.transactions.c.id, db.categories.c.name, db.tags.c.name)
            .order_by(order_by)
            .where(db.transactions.c.user_id == 2)  # hardcoded to 2 currently because no login
    )

    # filter only if id parameter is passed
    if id != 0:
        stmt = stmt.where(db.transactions.c.id == id)

    # filter only if place parameter is passed
    if place != "":
        stmt = stmt.where(db.transactions.c.place.ilike(f"%{place}%"))

    # filter only if category parameter is passed
    if category != "":
        stmt = stmt.where(db.categories.c.name.ilike(f"%{category}%"))

    # filter by start and end date
    stmt = stmt.where(sqlalchemy.between(db.transactions.c.transaction_date, start_date, end_date))

    # filter by min and max price
    stmt = stmt.where(sqlalchemy.between(db.transactions.c.amount, min_price, max_price))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "transaction_id": row.id,
                    "created_at": row.created_at,
                    "user_id": row.user_id,
                    "category": row.category_name,
                    "date": row.transaction_date,
                    "place": row.place,
                    "amount": row.amount,
                    "tag": row.tag_name,
                    "note": row.note,
                }
            )

    return json
