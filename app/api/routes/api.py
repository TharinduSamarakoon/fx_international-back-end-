from fastapi import APIRouter

from .authenticaion import router as auth_router
from .users import router as user_router
from .files import router as files
from .fundamental import router as fundamental
from .technical import router as technical
from .charts import router as charts
from .orders import router as orders
from .system import router as system_router
from .face import router as face

router = APIRouter()
router.include_router(auth_router, prefix="/oauth")
router.include_router(user_router, prefix="/users")
router.include_router(files, prefix="/files")
router.include_router(fundamental, prefix="/fundamental")
router.include_router(technical, prefix="/technical")
router.include_router(orders, prefix="/orders")
router.include_router(charts, prefix="/charts")
router.include_router(face, prefix="/face")
router.include_router(system_router)
