from datetime import datetime
from traceback import format_exception
from typing import Any, Callable, Dict, Union
from ...config import DataType


class Error(object):
    
    # __slots__ = [
    #     "__target",
    #     "__exception",
    #     "__callback",
    #     "__handler",
    #     "__timestamp",
    #     "__type",
    # ]

    def __init__(
        self,
        target: Any,
        exception: BaseException,
        callback: Callable,
        handler: Callable,
        **kwargs: Any,
    ) -> None:
        self.timestamp = kwargs.get("timestamp", datetime.now())
        self.type = DataType.ERROR
        self.target = target
        self.exception = exception
        self.callback = callback
        self.handler = handler

    def json(self, flat: bool = False) -> Dict[str, Union[str, int, float, dict]]:
        # TODO
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"Error( timestamp={self.timestamp}, callback={self.callback}, handler={self.handler}, exception={format_exception(type(self.exception), self.exception, self.exception.__traceback__)})"
