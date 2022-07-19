import jwt
import logging

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from ..crud.users import get_user
from ..db.mongodb import AsyncIOMotorClient, get_database
from ..models.token import TokenPayload
from ..models.user import User

from ..config import JWT_TOKEN_PREFIX, SECRET_KEY

logger = logging.getLogger("uvicorn.error")

ALGORITHM = "HS256"
access_token_jwt_subject = "access"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/token")


def _get_authorization_token(authorization: str = Header(...)):
    token_prefix, token = authorization.split(" ")
    if token_prefix != JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid authorization type"
        )

    return token


async def get_current_user(db: AsyncIOMotorClient = Depends(get_database),
                           token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    dbuser = await get_user(db, token_data.username)
    if not dbuser:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    user = User(**dbuser.dict())
    return user


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt
