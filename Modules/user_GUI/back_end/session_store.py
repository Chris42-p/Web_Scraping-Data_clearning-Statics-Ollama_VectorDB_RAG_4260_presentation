import secrets

SESSION_STORE = {}

def create_session():
    session_id = secrets.token_urlsafe(32)
    SESSION_STORE[session_id] = {}

    return session_id