import datetime
from enum import Enum
import pytz
import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import src.database as db

router = APIRouter()


@router.get("/tags/", tags=["tags"])
def get_tags():
    """
    This endpoint returns all tags for the current user (currently
    hardcoded to user.id = 2 as logins are not implemented)
    """
    stmt = (
        sqlalchemy.select(
            db.tags.c.id,
            db.tags.c.created_at,
            db.tags.c.user_id,
            db.tags.c.name
        )
            .where(db.tags.c.user_id == 2)  # hardcoded to 2 currently because no login
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
def create_tag(name: str):
    """
    This endpoint adds a tag to the current user (currently hardcoded
    to user.id = 2 as logins are not implemented).

    The endpoint returns the id of the resulting tag that was created
    """
    with db.engine.begin() as conn:
        # Insert tag into tags table
        tag_values = {
          "user_id": 2,  # hardcoded at the moment
          "name": name
        }
        tag_stmt = db.tags.insert().values(tag_values).returning(db.tags.c.id)
        tag_result = conn.execute(tag_stmt)
        inserted_id = tag_result.fetchone()[0]
    return inserted_id


@router.delete("/tags/", tags=["tags"])
def remove_tag(id: int):
    """
    This endpoint removes the tag with the given tag id for the current
    user (currently hardcoded to user.id = 2 as logins are not implemented)
    """
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.select(db.tags.c.id).where(db.tags.c.id == id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="tag not found")
    stmt = sqlalchemy.delete(db.tags).where(db.tags.c.id == id)
    stmt = stmt.where(db.tags.c.user_id == 2)  # hardcoded to 2 currently because no login
    with db.engine.begin() as conn:
        conn.execute(stmt)
    return {"message": "Tag deleted successfully"}
