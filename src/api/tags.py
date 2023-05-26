import datetime
from enum import Enum
import pytz
import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import src.database as db
from src.access_ctrl import check_logged_in

router = APIRouter()


@router.get("/tags/", tags=["tags"])
def get_tags(session_key: str):
    """
    This endpoint returns all tags for the current user.
    """
    userId = check_logged_in(session_key)
    if userId is None:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to access this endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )
    stmt = (
        sqlalchemy.select(
            db.tags.c.id,
            db.tags.c.created_at,
            db.tags.c.user_id,
            db.tags.c.name
        )
            .where(db.tags.c.user_id == userId)
            .order_by(db.tags.c.id)
    )
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "tag_id": row.id,
                    "created_at": row.created_at,
                    "user_id": row.user_id,
                    "name": row.name,
                }
            )
    return json


@router.post("/tags/", tags=["tags"])
def create_tag(session_key: str, name: str):
    """
    This endpoint adds a tag to the current user.

    The endpoint returns the id of the resulting tag that was created
    """
    userId = check_logged_in(session_key)
    if userId is None:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to access this endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )
    with db.engine.begin() as conn:
        # Insert tag into tags table
        tag_values = {
          "user_id": userId,
          "name": name
        }
        tag_stmt = db.tags.insert().values(tag_values).returning(db.tags.c.id)
        tag_result = conn.execute(tag_stmt)
        inserted_id = tag_result.fetchone()[0]
    return inserted_id


#@router.delete("/tags/", tags=["tags"])
def remove_tag(session_key: str, id: int):
    """
    This endpoint removes the tag with the given tag id for the current user.
    """
    userId = check_logged_in(session_key)
    if userId is None:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to access this endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.select(db.tags.c.id).where(db.tags.c.id == id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="tag not found")
    stmt = sqlalchemy.delete(db.tags).where(db.tags.c.id == id)
    stmt = stmt.where(db.tags.c.user_id == userId)
    with db.engine.begin() as conn:
        conn.execute(stmt)
    return {"message": "Tag deleted successfully"}
