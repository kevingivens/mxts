from abc import ABCMeta
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from mxts.core import Order, Position


class OrderEntry:
    """mixin class to represent the sink side of an exchange
    
     TODO: add implementation logic if possible
    """

    #async def accounts(self) -> List[Account]:  # TODO List[Account] ?
    #    """get accounts from source"""
    #    return []

    #async def balance(self) -> Instrument:
    #    """get cash balance"""
    #    return []

    async def new_order(self, order: Order) -> bool:
        """Submit a new order to the exchange. 
           Should set the given order's `id` field to exchange-assigned id
        Args:
            order (Order)
        Returns:
            True if order received
            False if order rejected
        For MarketData-only, can just return False/None
        """
        raise NotImplementedError()

    async def cancel_order(self, order: Order) -> bool:
        """cancel a previously submitted order to the exchange.
        Args:
            order (Order)
        Returns:
            True if order received
            False if order rejected
        For MarketData-only, can just return False/None
        """
        raise NotImplementedError()