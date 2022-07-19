from fastapi import APIRouter


from ...config import API_NAME, SECRET_KEY
from ...utils import build_response

router = APIRouter()


@router.get("/health")
async def health_check():
    return await build_response(f"{API_NAME} is running")



