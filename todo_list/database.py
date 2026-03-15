import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()
load_dotenv(BASE_DIR / ".env")


def local_db_config():
    return {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("LOCAL_DB_NAME", "todo_list"),
            "USER": os.getenv("LOCAL_DB_USER", "developuser"),
            "PASSWORD": os.getenv("LOCAL_DB_PASSWORD", ""),
            "HOST": os.getenv("LOCAL_DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("LOCAL_DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }


def azure_db_config():
    return {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("AZURE_DB_NAME", "todo_list"),
            "USER": os.getenv("AZURE_DB_USER", ""),
            "PASSWORD": os.getenv("AZURE_DB_PASSWORD", ""),
            "HOST": os.getenv("AZURE_DB_HOST", ""),
            "PORT": os.getenv("AZURE_DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "ssl": {
                    "ca": str(BASE_DIR / "azure-mysql-ca.pem"),
                },
            },
        }
    }


def get_databases():
    if DJANGO_ENV == "local":
        return local_db_config()
    if DJANGO_ENV in {"azure", "test", "prod", "production"}:
        return azure_db_config()
    raise ValueError(f"Unsupported DJANGO_ENV: {DJANGO_ENV}")


DATABASES = get_databases()
print(DATABASES)