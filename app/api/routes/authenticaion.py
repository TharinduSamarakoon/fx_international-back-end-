from datetime import timedelta

from fastapi import APIRouter, Body, Depends
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from ...config import ACCESS_TOKEN_EXPIRE_MINUTES
from ...services.jwt import create_access_token
from ...crud.users import get_user_by_email
from ...db.mongodb import AsyncIOMotorClient, get_database
from ...models.user import UserInLogin
from ...utils import build_response

router = APIRouter()


@router.post("/token", tags=["authentication"])
async def login(user: UserInLogin, db: AsyncIOMotorClient = Depends(get_database)):
    db_user = await get_user_by_email(db, user.email)
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"username": db_user.username}, expires_delta=access_token_expires
    )
    return await build_response({"access_token": token})
