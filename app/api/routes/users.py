from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_201_CREATED
from fastapi.security.oauth2 import OAuth2PasswordBearer

from ...services.jwt import get_current_user
from ...services.users import check_free_username_and_email
from ...crud.users import update_user, create_user, get_all_users
from ...db.mongodb import AsyncIOMotorClient, get_database
from ...models.user import User, UserInUpdate, UserInCreate
from ...utils import build_response

router = APIRouter()


@router.get("/me", tags=["users"])
async def retrieve_current_user(user: User = Depends(get_current_user)):
    return await build_response(jsonable_encoder(user, by_alias=False))


@router.post("", tags=["users"], status_code=HTTP_201_CREATED)
async def register(user: UserInCreate,
                   db: AsyncIOMotorClient = Depends(get_database)):
    await check_free_username_and_email(db, user.username, user.email)

    async with await db.start_session() as s:
        async with s.start_transaction():
            await create_user(db, user)
            return await build_response("User created successfully", 201)


@router.put("", tags=["users"])
async def update_current_user(user: UserInUpdate,
                              current_user: User = Depends(get_current_user),
                              db: AsyncIOMotorClient = Depends(get_database)):
    if user.username == current_user.username:
        user.username = None
    if user.email == current_user.email:
        user.email = None

    await check_free_username_and_email(db, user.username, user.email)

    db_user = await update_user(db, current_user.username, user)
    return await build_response(jsonable_encoder(User(**db_user.dict()), by_alias=True))


@router.get("")
async def get_users(db: AsyncIOMotorClient = Depends(get_database)):
    users = await get_all_users(db)
    return await build_response(jsonable_encoder(users, by_alias=False))
