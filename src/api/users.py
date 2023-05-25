import sqlalchemy
from fastapi import APIRouter, HTTPException
from enum import Enum

from sqlalchemy.sql.operators import as_
from src import access_ctrl, database as db
from fastapi.params import Query
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

import bcrypt

router = APIRouter()


@router.post("/login/", tags=["access control"])
def post_login(username: str, password: str):
    """
    This endpoint logs in the specified user and starts a session, returning the session key.
    The session key is required to access most endpoints involving personal data.
    A session expires after 15 minutes of inactivity
    * `username`: The start of this budget period.
    * `end_date`: The end of this budget period.
    * `amount`: How much money.
    * `period_id`: The period id defined for this budget (1: Weekly, 4: Quarterly, etc.)
    """
    # TODO: login
    # if not access_ctrl.check_logged_in(user_id):
    #     raise HTTPException(401, "Not logged in")


    stmt = sqlalchemy.select(
        db.users.c.id,
        db.users.c.password_hash,
        db.users.c.password_salt
    ).where(db.users.c.username == username)
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(stmt)
            row = result.one()
            uid = row.id
            pass_hash = row.password_hash
            pass_salt = row.password_salt
    except:
        return {
            "token" : None,
            "status": "User not found"
        }
    # Check password
    # bcrypt stores the password hash and salt in the same output

    if bcrypt.checkpw(password.encode(), pass_hash.encode()):
        token = access_ctrl.login(uid)
        return {
            "token" : token,
            "id" : uid,
            "status": "Logged in successfully"
        }

    return {
        "token" : None,
        "status": "Incorrect password"
    }


@router.post("/logout/", tags=["access control"])
def post_logout(session_key):
    """
    This endpoint logs in the specified user and starts a session, returning the session key.
    The session key is required to access most endpoints involving personal data.
    A session expires after 15 minutes of inactivity
    * `username`: The start of this budget period.
    * `end_date`: The end of this budget period.
    * `amount`: How much money.
    * `period_id`: The period id defined for this budget (1: Weekly, 4: Quarterly, etc.)
    """
    if not access_ctrl.check_logged_in(session_key):
        raise HTTPException(401, "Not logged in")

    access_ctrl.logout(session_key)

class UserJson(BaseModel):
    username: str
    password: str

@router.post("/accounts/", tags=["access control"])
def add_user(user: UserJson):
    """
    This endpoint creates a new user
    """

    pw_salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(user.password.encode(), pw_salt)

    try:
        with db.engine.begin() as conn:
            values = {
                "username" : user.username,
                "password_hash" : pw_hash.decode(),
                "password_salt" : pw_salt.decode()
            }
            stmt = db.users.insert().values(values).returning(db.users.c.id)
            result = conn.execute(stmt)
            inserted_id = result.one().id
    except Exception as e:
        raise HTTPException(422, str(e))

    return inserted_id

