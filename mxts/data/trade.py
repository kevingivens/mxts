from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from .order import Order
from ..instrument import Instrument
from ..exchange import ExchangeType
from ...config import DataType, Side


class Trade(object):
    
    #__slots__ = [
    #    "id",
    #    "type",
    #    "price",
    #    "volume",
    #    "maker_orders",
    #    "taker_order",
    #    "my_order",
    #    "slippage",
    #    "transaction_cost",
    #]

    # Types = DataType

    def __init__(
        self,
        volume: float,
        price: float,
        taker_order: Order,
        maker_orders: Optional[List[Order]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = kwargs.get(
            "id", "0"
        )  # on construction, provide no ID until exchange assigns one
        self.type = DataType.TRADE

        assert isinstance(price, (float, int))
        assert isinstance(volume, (float, int))
        assert isinstance(taker_order, Order)
        assert volume == taker_order.filled

        self.price = price
        self.volume = volume
        self.maker_orders = maker_orders or []
        self.taker_order = taker_order

        self.my_order = kwargs.get("my_order", None)
        self.slippage = 0.0
        self.transaction_cost = 0.0

    @property
    def timestamp(self) -> datetime:
        return self.taker_order.timestamp

    @property
    def instrument(self) -> Instrument:
        return self.taker_order.instrument

    @property
    def exchange(self) -> ExchangeType:
        return self.taker_order.exchange

    @property
    def side(self) -> Side:
        return self.taker_order.side

    @property
    def notional(self) -> float:
        return self.price * self.volume

    def finished(self) -> bool:
        return self.taker_order.finished()

    @id.setter
    def id(self, id: str) -> None:
        assert isinstance(id, (str, int))
        self.id = str(id)

    @my_order.setter
    def my_order(self, order: Order) -> None:
        assert isinstance(order, Order)
        self.__my_order = order

    def __repr__(self) -> str:
        return f"Trade( id={self.id}, timestamp={self.timestamp}, {self.volume}@{self.price}, \n\ttaker_order={self.taker_order},\n\tmaker_orders={self.maker_orders}, )"

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Trade)
        return self.id == other.id and self.timestamp == other.timestamp

    def json(self, flat: bool = False) -> Dict[str, Union[str, int, float, dict]]:
        """convert trade to flat json"""
        ret: Dict[str, Union[str, int, float, dict]] = {
            "id": self.id,
            "timestamp": self.timestamp.timestamp(),
            "price": self.price,
            "volume": self.volume,
        }

        if flat:
            # Typings here to enforce flatness of json
            taker_order: Dict[str, Union[str, int, float, dict]] = {
                "taker_order." + k: v
                for k, v in self.taker_order.json(flat=flat).items()
            }

            maker_orders: List[Dict[str, Union[str, int, float, dict]]] = [
                {"maker_order{}." + k: v for k, v in order.json(flat=flat).items()}
                for i, order in enumerate(self.maker_orders)
            ]

            # update with taker order dict
            ret.update(taker_order)

            # update with maker order dicts
            for maker_order in maker_orders:
                ret.update(maker_order)

        else:
            ret["taker_order"] = self.taker_order.json()  # type: ignore
            ret["maker_orders"] = [m.json() for m in self.maker_orders]  # type: ignore

        return ret

    @staticmethod
    def fromJson(jsn: dict) -> "Trade":
        ret = Trade(
            jsn["volume"],
            jsn["price"],
            Order.fromJson(jsn["taker_order"]),
            [Order.fromJson(x) for x in jsn["maker_orders"]],
        )

        if "id" in jsn:
            ret.id = str(jsn.get("id"))
        return ret

    @staticmethod
    def schema() -> Dict[str, Type]:
        # FIXME
        # this varies from the json schema
        return {"id": int, "timestamp": int, "volume": float, "price": float}
