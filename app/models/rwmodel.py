from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseConfig, BaseModel


class RWModel(BaseModel):
    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            ObjectId: lambda oid: str(oid)
        }
