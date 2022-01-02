from datetime import datetime
from typing import Mapping, Union, Type, Optional, Any, cast

from ..exchange import ExchangeType
from ..instrument import Instrument
from ..utils import id_gen
from ..config.enums   import DataType

_ID_GEN = id_gen()


class Data(object):
    __slots__ = [
        "id",
        "timestamp",
        "type",
        "instrument",
        "exchange",
        "data",
    ]

    def __init__(
        self,
        instrument: Optional[Instrument] = None,
        exchange: ExchangeType = ExchangeType(""),
        data: dict = {},
        **kwargs: Union[int, datetime],
    ) -> None:
        self.id: int = cast(int, kwargs.get("id", _ID_GEN()))
        self.timestamp: datetime = cast(
            datetime, kwargs.get("timestamp", datetime.now())
        )

        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.type = DataType.DATA
        self.instrument = instrument
        self.exchange = exchange
        self.data = data

    def __repr__(self) -> str:
        return f"Data( id={self.id}, timestamp={self.timestamp}, instrument={self.instrument}, exchange={self.exchange})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Data):
            raise TypeError()
        return self.id == other.id

    def json(self) -> Mapping[str, Union[str, int, float]]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.timestamp(),
            "type": self.type.value,
            "instrument": str(self.instrument),
            "exchange": str(self.exchange),
        }