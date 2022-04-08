from datetime import datetime
#from traceback import format_exception
from typing import Any, Callable, Dict, Union

from pydantic import BaseModel
from ..config.enums import DataType

class Error(BaseModel):
    type: DataType = DataType.ERROR
    data: Any
    timestamp: datetime = datetime.now()
    exception: BaseException
    callback: Callable
