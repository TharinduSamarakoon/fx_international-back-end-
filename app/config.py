from databases import DatabaseURL
from starlette.config import Config

VERSION = "v0.1"
API_PREFIX = f"/api/{VERSION}"
API_NAME = "API"

JWT_TOKEN_PREFIX = "Token"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

config = Config(".env")
DEBUG: bool = config("DEBUG", cast=bool, default=True)
# openssl rand -hex 32
SECRET_KEY = "83cd07fdf2c8311cd4ff3d8b4b9aa6d1c3895bfd6fec1a707dba551b1e021bf4"
"""
Database Configurations
"""
MONGO_HOST: str = config("MONGO_HOST", cast=str, default="localhost")
MONGO_PORT = config("MONGO_PORT", cast=int, default=27017)
MONGO_DB = config("MONGO_DB", cast=str, default="forexInternational")
MONGO_USERNAME = config("MONGO_USERNAME", cast=str, default=None)
MONGO_PASSWORD = config("MONGO_PASSWORD", cast=str, default="")

if MONGO_USERNAME is not None:
    MONGODB_URL = DatabaseURL(
        f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
    )
else:
    MONGODB_URL = DatabaseURL(
        f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
    )
MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

database_name = MONGO_DB
users_collection = "users"
