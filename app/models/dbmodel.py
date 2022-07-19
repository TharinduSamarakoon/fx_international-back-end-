from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, BaseConfig


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DBModelMixin(DateTimeModelMixin):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    id: ObjectId = Field(default=ObjectId(), alias='_id')
