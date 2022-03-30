from abc import ABCMeta
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mxts.core import Order, Position


class OrderEntry:
    """mixin class to represent the rest-sink
    side of a data source"""

    async def accounts(self) -> List[Position]:  # TODO List[Account] ?
        """get accounts from source"""
        return []

    async def balance(self) -> List[Position]:
        """get cash balance"""
        return []

    async def new_order(self, order: Order) -> bool:
        """submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id
        Returns:
            True if order received
            False if order rejected
        For MarketData-only, can just return False/None
        """
        raise NotImplementedError()

    async def cancel_order(self, order: Order) -> bool:
        """cancel a previously submitted order to the exchange.
        Returns:
            True if order received
            False if order rejected
        For MarketData-only, can just return False/None
        """
        raise NotImplementedError()