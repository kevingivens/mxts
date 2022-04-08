from typing import Any

from pydantic import BaseModel
from ..config import EventType


class Event(BaseModel):
    # TODO: check slots behavour of BaseModel
    type: EventType
    data: Any