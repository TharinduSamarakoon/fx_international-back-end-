from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from ...db.mongodb import get_database
from ...models.user import User
from ...services.jwt import get_current_user
from ...services.order import create_order
from ...utils import build_response

router = APIRouter()


@router.post("")
async def post_order(symbol: str, currency: str, action: int, user: User = Depends(get_current_user),
                     db: AsyncIOMotorClient = Depends(get_database)):
    await create_order(symbol, currency, action, user, db)
    return await build_response("Order created")
