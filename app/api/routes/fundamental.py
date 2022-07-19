import json
from fastapi import APIRouter, Depends

from ...models.user import User
from ...services.fundamental import get_fundamental_analysis
from ...services.jwt import get_current_user
from ...utils import build_response

router = APIRouter()


@router.get("")
async def get_fundamental_data(user: User = Depends(get_current_user)):
    data = await get_fundamental_analysis()
    sorted_json = data.to_json(orient="records", date_format="iso")
    return await build_response(json.loads(sorted_json))
