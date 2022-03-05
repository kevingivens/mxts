from datetime import datetime
from typing import Any, Mapping, Optional, Type, Union, cast

from ...config import DataType, OrderFlag, OrderType, Side
from ..exchange import ExchangeType
from ..instrument import Instrument


class Order(object):
    
    #__slots__ = [
    #    "id",
    #    "timestamp",
    #    "type",
    #    "instrument",
    #    "exchange",
    #    "volume",
    #    "price",
    #    "notional",
    #    "filled",
    #    "side",
    #    "order_type",
    #    "flag",
    #    "stop_target",
    #    "force_done",
    #]
    
    def __init__(
        self,
        volume: float,
        price: float,
        side: Side,
        instrument: Instrument,
        exchange: ExchangeType = ExchangeType(""),
        notional: float = 0.0,
        order_type: OrderType = OrderType.MARKET,
        flag: OrderFlag = OrderFlag.NONE,
        stop_target: Optional["Order"] = None,
        **kwargs: Any,
    ) -> None:
        self.__id = kwargs.get(
            "id", 0
        )  # on construction, provide no ID until exchange assigns one
        self.timestamp = kwargs.get("timestamp") or datetime.now()
        self.type = DataType.ORDER

        assert isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.instrument = instrument
        self.exchange = exchange

        assert isinstance(volume, (int, float))
        assert volume < float("inf") and (
            (volume > 0 and order_type != OrderType.STOP)
            or (order_type == OrderType.STOP and volume == 0)
        )
        assert order_type == OrderType.STOP or (
            (volume > 0.0) and (volume < float("inf"))
        )
        assert isinstance(price, (int, float))
        assert price < float("inf")
        assert isinstance(side, Side)
        assert isinstance(notional, (int, float))
        assert isinstance(order_type, OrderType)
        assert isinstance(flag, OrderFlag)
        assert (order_type != OrderType.STOP and stop_target is None) or (
            isinstance(stop_target, Order)
            and order_type == OrderType.STOP
            and stop_target.order_type != OrderType.STOP
        )
        assert order_type != OrderType.STOP or (
            isinstance(cast(Order, stop_target).instrument, Instrument)
        )

        self.volume = round(volume, 8)
        self.price = round(price, 4)
        self.side = side
        self.notional = notional
        self.order_type = order_type
        self.flag = flag
        self.stop_target = stop_target

        self.filled = kwargs.get("filled", 0.0)
        self.force_done = False

    def finished(self) -> bool:
        return (self.volume == self.filled) or self.__force_done

    def finish(self) -> None:
        """force this order to mark itself as "finished", even if it
        isn't fully filled (e.g. with certain flags)"""
        self.force_done = True

    @id.setter
    def id(self, id: Union[str, int]) -> None:
        assert isinstance(id, (int, str))
        self.__id = str(id)

    @timestamp.setter
    def timestamp(self, timestamp: datetime) -> None:
        assert isinstance(timestamp, datetime)
        self.__timestamp = timestamp

    @volume.setter
    def volume(self, volume: float) -> None:
        assert isinstance(volume, (int, float))
        assert volume < float("inf") and (
            volume > 0 or self.order_type == OrderType.STOP
        )
        volume = round(volume, 8)

        assert volume >= self.filled

        self.volume = volume

    @filled.setter
    def filled(self, filled: float) -> None:
        assert isinstance(filled, (int, float))
        filled = round(filled, 8)
        assert filled <= self.volume
        self.filled = filled

    def __repr__(self) -> str:
        return f"Order( instrument={self.instrument}, timestamp={self.timestamp}, {self.volume}@{self.price}, side={self.side}, exchange={self.exchange})"

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Order)
        return (
            self.id == other.id
            and self.instrument == other.instrument
            and self.exchange == other.exchange
            and self.price == other.price
            and self.volume == other.volume
            and self.notional == other.notional
            and self.filled == other.filled
        )

    def json(self, flat: bool = False) -> Mapping[str, Union[str, int, float, dict]]:
        if flat:
            # TODO
            raise NotImplementedError()

        return {
            "id": self.id,
            "timestamp": self.timestamp.timestamp(),
            "volume": self.volume,
            "price": self.price,
            "side": self.side.value,
            "instrument": self.instrument.json(),
            "exchange": self.exchange.json(),
            "notional": self.notional,
            "filled": self.filled,
            "order_type": self.order_type.value,
            "flag": self.flag.value,
            "stop_target": self.stop_target.json()  # type: ignore
            if self.stop_target
            else "",
        }

    @staticmethod
    def fromJson(jsn: dict) -> "Order":
        kwargs = {}
        kwargs["volume"] = jsn["volume"]
        kwargs["price"] = jsn["price"]
        kwargs["side"] = Side(jsn["side"])
        kwargs["instrument"] = Instrument.fromJson(jsn["instrument"])
        kwargs["exchange"] = ExchangeType.fromJson(jsn["exchange"])

        if "notional" in jsn and jsn["notional"]:
            kwargs["notional"] = jsn["notional"]

        if "flag" in jsn and jsn["flag"]:
            kwargs["flag"] = OrderFlag(jsn["flag"])

        if "stop_target" in jsn and jsn["stop_target"]:
            kwargs["stop_target"] = Order.fromJson(jsn["stop_target"])

        if "order_type" in jsn and jsn["order_type"]:
            kwargs["order_type"] = OrderType(jsn["order_type"])

        if "notional" in jsn and jsn["notional"]:
            kwargs["notional"] = jsn["notional"]

        ret = Order(**kwargs)

        if "filled" in jsn and jsn["filled"]:
            ret.filled = jsn["filled"]

        return ret

    @staticmethod
    def schema() -> Mapping[str, Type]:
        return {
            "id": str,
            "timestamp": int,
            "volume": float,
            "price": float,
            "side": str,
            "instrument": str,
            "exchange": str,
        }
