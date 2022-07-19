import uuid

from fastapi import APIRouter, UploadFile, File

from ...services.face import verify_face
from ...utils import build_response

router = APIRouter()


@router.post("")
async def face(file: UploadFile = File(...)):
    file_name = uuid.uuid4()
    ext = file.filename.split(".")[-1]
    path = f"/tmp/{file_name}.{ext}"
    with open(path, "wb") as f:
        f.write(file.file.read())
    is_verified = await verify_face(path)
    return await build_response({"is_verified": is_verified})
