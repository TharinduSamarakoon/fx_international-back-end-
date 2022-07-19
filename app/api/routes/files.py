import uuid

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse, StreamingResponse

from ...utils import build_response

router = APIRouter()
key = 101


@router.get("/static/{filename}")
def get_file(filename: str):
    def iterfile():
        with open(f"app/static/{filename}", "rb") as f:
            encrypted = bytearray(f.read())
            for index, values in enumerate(encrypted):
                encrypted[index] = values ^ key
                yield bytes(encrypted)
            # with open(f"/tmp/{filename}", "wb") as fd:
            #     fd.write(encrypted)

    # return FileResponse(f"/tmp/{filename}")
    return StreamingResponse(iterfile(), media_type="image/jpeg")

@router.post("")
async def create_upload_file(file: UploadFile = File(...)):
    file_name = uuid.uuid4()
    ext = file.filename.split(".")[-1]
    path = f"app/static/{file_name}.{ext}"
    image = file.file.read()
    image = bytearray(image)
    for index, values in enumerate(image):
        image[index] = values ^ key
    with open(path, "wb") as f:
        f.write(image)
    return await build_response({"file_path": path.replace("app/", "")})
