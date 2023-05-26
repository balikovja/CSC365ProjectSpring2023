import sqlalchemy
from fastapi import APIRouter, HTTPException
from enum import Enum

from src import access_ctrl, database as db
from fastapi.params import Query
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

import bcrypt

router = APIRouter()

class UserJson(BaseModel):
    username: str
    password: str


@router.post("/login/", tags=["access control"])
def post_log_in(user: UserJson):
    """
    This endpoint logs in the specified user and starts a session, returning the session key.
    The session key is required to access most endpoints involving personal data.
    A session expires after 15 minutes of inactivity.
    Returns:
    * `token` : the session key (null if failed)
    * `id` : the internal user id
    * `status` : a status message
    """

    stmt = sqlalchemy.select(
        db.users.c.id,
        db.users.c.password_hash,
        db.users.c.password_salt
    ).where(db.users.c.username == user.username)
    
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

    if bcrypt.checkpw(user.password.encode(), pass_hash.encode()):
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
def post_log_out(session_key):
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


@router.post("/accounts/", tags=["access control"])
def add_user(user: UserJson):
    """
    This endpoint creates a new user
    """
    try:
        pw_salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(user.password.encode(), pw_salt)
    except:
        raise HTTPException(400)
    
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
        raise HTTPException(422, "Username invalid or has already been taken")

    return inserted_id

# TODO: implement. Requires foreign key cascade delete setup...
# @router.delete("/accounts/", tags=["access control"])
def delete_user(session_key: str, user: UserJson):
    """
    This endpoint deletes a user
    """
    raise NotImplementedError()
    try:
        pw_salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(user.password.encode(), pw_salt)
    except:
        raise HTTPException(400)
    
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
        raise HTTPException(422, "Username invalid or has already been taken")

    return inserted_id

