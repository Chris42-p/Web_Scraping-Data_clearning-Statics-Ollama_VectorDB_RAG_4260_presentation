APP_CONFIG = {
    "APP_NAME": "Big Data Analytics Platform API",
    "ALLOWED_ORIGINS": [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    "COOKIE_NAME": "session_id",
    "COOKIE_HTTPONLY": True,
    "COOKIE_SAMESITE": "lax",
    "COOKIE_SECURE": False,
    "DEFAULT_SEARCH_RESULTS": 5,
}

FEATURE_FLAGS = {
    "ENABLE_GMAIL": True,
    "ENABLE_SPIDER": True,
    "ENABLE_REPORTS": True,
    "ENABLE_FEEDBACK": True,
    "ENABLE_MODEL_RERUNNING": True,
}