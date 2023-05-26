import random
import datetime
import secrets

sessions = {}


# 15 minutes time out
LOGIN_TIME_OUT = datetime.timedelta(minutes=15)

SESS_KEY_BYTES = 10
GC_PROBABILITY = 1/20


def session_gc():
    for key, s in sessions.items():
        if expiredq(s["ts"]):
            sessions.pop(key)


def _dt_now() -> datetime.datetime:
    return datetime.datetime.now()


def expiredq(timestamp: datetime.datetime):
    return (_dt_now() - timestamp) > LOGIN_TIME_OUT


def check_logged_in(key):
    if key in sessions:
        if expiredq(sessions[key]["ts"]):
            sessions.pop(key)
            return None
        sessions[key]["ts"] = _dt_now()
        return sessions[key]["uid"]
    return None


def login(user_id):
    key = None
    while key is None or key in sessions:
        key = secrets.token_urlsafe(SESS_KEY_BYTES)
    sessions[key] = {
        "uid" : user_id,
        "ts" : _dt_now()
    }
    # occasionally clean up abandoned sessions
    if random.random() < GC_PROBABILITY:
        session_gc()
    return key


def logout(key):
    if key in sessions:
        sessions.pop(key)
