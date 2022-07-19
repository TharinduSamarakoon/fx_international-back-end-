import json

from fastapi import APIRouter

from ...services.chart import get_chart_data, get_indicator_val
from ...utils import build_response

router = APIRouter()


@router.get("/{symbol}/{currency}")
async def get_chart(symbol: str, currency: str):
    chart = await get_chart_data(symbol, currency)
    return await build_response(json.loads(chart))


@router.get("/indicator/{symbol}/{currency}")
async def get_indicator(symbol: str, currency: str):
    indicator = await get_indicator_val(symbol, currency)
    return await build_response({"value": indicator})
