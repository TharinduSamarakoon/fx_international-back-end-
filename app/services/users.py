import logging

from typing import Optional
from fastapi import HTTPException
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from ..crud.users import get_user, get_user_by_email
from ..db.mongodb import AsyncIOMotorClient

logger = logging.getLogger("uvicorn.error")


async def check_free_username_and_email(
        conn: AsyncIOMotorClient, username: Optional[str] = None, email: Optional[str] = None
):
    if username:
        user_by_username = await get_user(conn, username)
        if user_by_username:
            logger.error("User already exists")
            raise HTTPException(
                status_code=409,
                detail="User with this username already exists",
            )
    if email:
        user_by_email = await get_user_by_email(conn, email)
        if user_by_email:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists",
            )
