import logging

from motor.motor_asyncio import AsyncIOMotorClient
from ..config import MONGODB_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from .mongodb import db

logger = logging.getLogger("uvicorn.error")


async def connect_to_mongo():
    try:
        logger.info("Connecting to the database...")
        db.client = AsyncIOMotorClient(str(MONGODB_URL),
                                       maxPoolSize=MAX_CONNECTIONS_COUNT,
                                       minPoolSize=MIN_CONNECTIONS_COUNT)
        logger.info("Successfully connected to the database!")
    except ConnectionRefusedError:
        logger.error("Database connecting failed!")


async def close_mongo_connection():
    logger.info("Closing database connection...")
    db.client.close()
    logger.info("Database connection closed！")
