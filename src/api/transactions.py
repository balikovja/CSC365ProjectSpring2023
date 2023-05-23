import datetime
from enum import Enum
import pytz
import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import src.database as db

router = APIRouter()


class TransactionJson(BaseModel):
    category: int
    date: datetime.date
    place: str
    amount: float
    tag: int
    note: str


@router.post("/transactions/", tags=["transactions"])
def add_transaction(transaction: TransactionJson):
    """
    This endpoint adds a transaction to the current user (currently hardcoded
    to user.id = 2 as logins are not implemented). The transaction is represented
    by the category_id, the transaction_date, the place it occurred, the amount,
    the tag, and a note.

    The endpoint ensures that a valid category was chosen

    The endpoint ensures that a valid tag was chosen

    The endpoint returns the id of the resulting transaction that was created
    """
    # Set your timezone
    tz = pytz.timezone('America/Los_Angeles')

    # Get the current time in your timezone
    current_time = datetime.datetime.now(tz)

    # Convert the datetime to ISO 8601 format
    iso_time = current_time.isoformat()

    with db.engine.begin() as conn:
        stmt = sqlalchemy.select(db.categories.c.id).where(db.categories.c.id == transaction.category)
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=400, detail="invalid category (use get_categories)")
        else:
            row = result.fetchone()
            categoryID = row[0]
        stmt = sqlalchemy.select(db.tags.c.id).where(db.tags.c.id == transaction.tag)
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=400, detail="invalid tag (use get_tags or create_tag)")
        else:
            row = result.fetchone()
            tagID = row[0]
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


@router.delete("/transactions/", tags=["transactions"])
def remove_transaction(id: int):
    """
    This endpoint removes the transaction with the given transaction id for the
    current user (currently hardcoded to user.id = 2 as logins are not implemented)
    """
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.select(db.transactions.c.id).where(db.transactions.c.id == id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="transaction not found")
    stmt = sqlalchemy.delete(db.transactions).where(db.transactions.c.id == id)
    stmt = stmt.where(db.transactions.c.user_id == 2)  # hardcoded to 2 currently because no login
    with db.engine.begin() as conn:
        conn.execute(stmt)
    return {"message": "Transaction deleted successfully"}


class transaction_sort_options(str, Enum):
    dateNewToOld = "dateNewToOld"
    dateOldToNew = "dateOldToNew"
    priceLowToHigh = "priceLowToHigh"
    priceHighToLow = "priceHighToLow"
    category = "category"
    place = "place"


@router.get("/transactions/", tags=["transactions"])
def get_transactions(
        id: int = None,
        category: int = None,
        place: str = None,
        tag: int = None,
        start_date: datetime.date = datetime.date(1, 1, 1),
        end_date: datetime.date = datetime.date.today(),
        min_amount: float = 0,
        max_amount: float = 10000000,
        sort: transaction_sort_options = transaction_sort_options.dateNewToOld,
):
    """
    This endpoint returns transactions of the current user that fit with
    the given arguments, sorted by the given sort type.
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
            .join(db.tags, db.tags.c.id == db.transactions.c.tag_id, isouter=True)
            .group_by(db.transactions.c.id, db.categories.c.name, db.tags.c.name)
            .order_by(order_by)
            .where(db.transactions.c.user_id == 2)  # hardcoded to 2 currently because no login
    )

    # filter only if id parameter is passed
    if id is not None:
        stmt = stmt.where(db.transactions.c.id == id)

    # filter only if place parameter is passed
    if place is not None:
        stmt = stmt.where(db.transactions.c.place.ilike(f"%{place}%"))

    # filter only if category parameter is passed
    if category is not None:
        stmt = stmt.where(db.categories.c.id == category)

    if tag is not None:
        stmt = stmt.where(db.tags.c.id == tag)

    # filter by start and end date
    stmt = stmt.where(sqlalchemy.between(db.transactions.c.transaction_date, start_date, end_date))

    # filter by min and max price
    stmt = stmt.where(sqlalchemy.between(db.transactions.c.amount, min_amount, max_amount))

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


@router.put("/transactions/{id}", tags=["transactions"])
def update_transaction(
        id: int = None,
        category: int = None,
        tag: int = None,
        place: str = None,
        date: datetime.date = None,
        amount: float = None
):
    """
    This endpoint updates a transaction of the given id of the current user
    (currently hardcoded to user.id = 2 as logins are not implemented). If any
    of the accepted values (besides id) is changed from its default, the
    transaction will have that value updated.
    e.g. If you enter a valid id, and enter "Vons" for place, place will be
    updated to "Vons" in the transaction with the given id

    The endpoint ensures that a valid category was chosen, if one was chosen

    The endpoint ensures that a valid tag was chosen, if one was chosen
    """
    with db.engine.begin() as conn:
        stmt = sqlalchemy.select(db.transactions).where(db.transactions.c.id == id)
        stmt = stmt.where(db.transactions.c.user_id == 2)  # hardcoded user_id
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="transaction not found")
        db_transaction = result.fetchone()
        if category is not None:
            stmt = sqlalchemy.select(db.categories.c.id).where(db.categories.c.id == category)
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail="invalid category (use get_categories)")
            else:
                stmt = (
                    sqlalchemy.update(db.transactions)
                        .values(category_id=category)
                        .where(db.transactions.c.id == id)
                )
                conn.execute(stmt)
        if tag is not None:
            stmt = sqlalchemy.select(db.tags.c.id).where(db.tags.c.id == tag)
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail="invalid tag (use get_tags or create_tag)")
            else:
                stmt = (
                    sqlalchemy.update(db.transactions)
                        .values(tag_id=category)
                        .where(db.transactions.c.id == id)
                )
                conn.execute(stmt)
        if date is not None:
            stmt = (
                sqlalchemy.update(db.transactions)
                    .values(transaction_date=date)
                    .where(db.transactions.c.id == id)
            )
            conn.execute(stmt)
        if place is not None:
            stmt = (
                sqlalchemy.update(db.transactions)
                    .values(place=place)
                    .where(db.transactions.c.id == id)
            )
            conn.execute(stmt)
        if amount is not None:
            stmt = (
                sqlalchemy.update(db.transactions)
                    .values(amount=amount)
                    .where(db.transactions.c.id == id)
            )
            conn.execute(stmt)
    return {"message": "Transaction updated successfully"}


@router.put("/transactions/{id}/split", tags=["transactions"])
def split_transaction(
        id: int,
        transaction1_amount: int,
        transaction1_category: int,
        transaction2_amount: int,
        transaction2_category: int,
        transaction1_tag: int = None,
        transaction2_tag: int = None
):
    """
    This endpoint splits a transaction of the given id of the current user
    (currently hardcoded to user.id = 2 as logins are not implemented) into
    2 separate transactions with the given amounts, categories, and tags.

    The endpoint ensures the two given amounts sum to the given transaction's
    amount.

    The endpoint ensures that valid categories were chosen.

    The endpoint ensures that valid tags were chosen, if chosen
    """
    with db.engine.begin() as conn:
        stmt = sqlalchemy.select(db.transactions).where(db.transactions.c.id == id)
        stmt = stmt.where(db.transactions.c.user_id == 2)  # hardcoded user_id
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="transaction not found")
        db_transaction = result.fetchone()
        if db_transaction.amount != (transaction1_amount + transaction2_amount):
            raise HTTPException(status_code=400, detail="Given amounts do not sum to given transaction's total")
        # verify trans1 category
        stmt = sqlalchemy.select(db.categories.c.id).where(db.categories.c.id == transaction1_category)
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=400, detail="invalid transaction1_category (use get_categories)")
        else:
            row = result.fetchone()
            categoryID1 = row[0]
        # verify trans2 category
        stmt = sqlalchemy.select(db.categories.c.id).where(db.categories.c.id == transaction2_category)
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=400, detail="invalid transaction2_category (use get_categories)")
        else:
            row = result.fetchone()
            categoryID2 = row[0]
        # verify trans1 tag
        if transaction1_tag is not None:
            stmt = sqlalchemy.select(db.tags.c.id).where(db.tags.c.id == transaction1_tag)
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail="invalid transaction1_tag (use get_tags or create_tag)")
            else:
                row = result.fetchone()
                tagID1 = row[0]
        else:
            tagID1 = 0
        # verify trans2 tag
        if transaction2_tag is not None:
            stmt = sqlalchemy.select(db.tags.c.id).where(db.tags.c.id == transaction2_tag)
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail="invalid transaction2_tag (use get_tags or create_tag)")
            else:
                row = result.fetchone()
                tagID2 = row[0]
        else:
            tagID2 = 0
        # Time to add two new transactions
        newTrans1 = add_transaction(TransactionJson(
            category=categoryID1,
            date=db_transaction.transaction_date,
            place=db_transaction.place,
            amount=transaction1_amount,
            tag=tagID1,
            note=db_transaction.note
        ))
        newTrans2 = add_transaction(TransactionJson(
            category=categoryID2,
            date=db_transaction.transaction_date,
            place=db_transaction.place,
            amount=transaction2_amount,
            tag=tagID2,
            note=db_transaction.note
        ))
        # remove original transaction
        remove_transaction(id=id)
    return newTrans1, newTrans2
