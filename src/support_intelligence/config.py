import os


def get_app_env() -> str:
    return os.getenv("APP_ENV", "development")
