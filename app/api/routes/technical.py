from fastapi import APIRouter

from ...services.technical import get_technical_action
from ...utils import build_response

router = APIRouter()


@router.get("/{symbol}/{currency}")
async def get_technical_analyse(symbol: str, currency: str):
    res = await get_technical_action(symbol, currency)
    return await build_response({"action":res})
