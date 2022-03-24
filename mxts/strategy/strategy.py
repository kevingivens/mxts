import asyncio
from abc import abstractmethod
from typing import Any, List
# from .calculations import CalculationsMixin
from .portfolio import StrategyPortfolioMixin
# from .risk import StrategyRiskMixin
# from .utils import StrategyUtilsMixin
from ..config import Side
from ..core import Event, EventHandler, Order, Instrument
from ..utils import id_generator


class Strategy(
    EventHandler,
    #StrategyUtilsMixin,
    StrategyPortfolioMixin,
    #StrategyRiskMixin,
    #CalculationsMixin,
):
    # _ID_GENERATOR = id_generator()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore
        # self.__inst = Strategy._ID_GENERATOR()

    def name(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return "<{self.__class__.__name__}>"

    #########################
    # Event Handler Methods #
    #########################
    @abstractmethod
    async def on_trade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""

    async def on_order(self, event: Event) -> None:
        """Called whenever an Order `Open`, `Cancel`, `Change`, or `Fill` event is received"""
        pass

    async def on_open(self, event: Event) -> None:
        """Called whenever an Order `Open` event is received"""
        pass

    async def on_cancel(self, event: Event) -> None:
        """Called whenever an Order `Cancel` event is received"""
        pass

    async def on_change(self, event: Event) -> None:
        """Called whenever an Order `Change` event is received"""
        pass

    async def on_fill(self, event: Event) -> None:
        """Called whenever an Order `Fill` event is received"""
        pass

    async def on_data(self, event: Event) -> None:
        """Called whenever other data is received"""
        pass

    async def on_halt(self, event: Event) -> None:
        """Called whenever an exchange `Halt` event is received, i.e. an event to stop trading"""
        pass

    async def on_continue(self, event: Event) -> None:
        """Called whenever an exchange `Continue` event is received, i.e. an event to continue trading"""
        pass

    async def on_error(self, event: Event) -> None:
        """Called whenever an internal error occurs"""
        pass

    async def on_start(self, event: Event) -> None:
        """Called once at engine initialization time"""
        pass

    async def on_exit(self, event: Event) -> None:
        """Called once at engine exit time"""
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def on_bought(self, event: Event) -> None:
        """callback method for if your order executes (buy)

        Args:
            trade (Trade): the trade/s as your order completes
        """
        pass

    async def on_sold(self, event: Event) -> None:
        """callback method for if your order executes (sell)

        Args:
            trade (Trade): the trade/s as your order completes
        """
        pass

    async def on_traded(self, event: Event) -> None:
        """callback method for if your order executes (either buy or sell)

        Args:
            trade (Trade): the trade/s as your order completes
        """
        pass

    async def on_rejected(self, event: Event) -> None:
        """callback method for if your order fails to execute

        Args:
            order (Order): the order you attempted to make
        """
        pass

    async def on_canceled(self, event: Event) -> None:
        """callback method for if your order is canceled

        Args:
            order (Order): the order you canceled
        """
        pass

    #######################
    # Order Entry Methods #
    #######################
    async def new_order(self, order: Order) -> bool:
        """helper method, defers to buy/sell"""
        # defer to execution
        return await self._manager.new_order(self, order)

    async def cancel_order(self, order: Order) -> bool:
        """cancel an open order

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        """
        # defer to execution
        return await self._manager.cancel_order(self, order)

    async def cancel(self, order: Order) -> bool:
        """cancel an open order

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        """
        # defer to execution
        return await self._manager.cancel_order(self, order)

    async def buy(self, order: Order) -> bool:
        """submit a buy order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `bought` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        """
        return await self._manager.newOrder(self, order)

    async def sell(self, order: Order) -> bool:
        """submit a sell order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `sold` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        """
        return await self._manager.newOrder(self, order)

    async def cancel_all(self, instrument: Instrument = None) -> List[bool]:
        """cancel all open orders. If argument is provided, cancel only orders for
        that instrument.

        Args:
            insrument (Optional[Instrument]): Cancel all orders that trade this instrument
        Returns:
            None
        """
        orders = self.orders(instrument=instrument)
        if orders:
            return await asyncio.gather(*(self.cancel(order) for order in orders))
        return []

    async def close_all(self, instrument: Instrument = None) -> List[bool]:
        """close all open postions immediately. If argument is provided, close only positions for
        that instrument.

        Args:
            insrument (Optional[Instrument]): Close all positions for this instrument
        Returns:
            None
        """
        # cancel all open orders
        await self.cancel_all(instrument=instrument)

        # construct closing orders
        orders = [
            Order(
                volume=p.size,
                price=0,
                side=Side.SELL if p.size > 0 else Side.BUY,
                instrument=p.instrument,
                exchange=p.exchange,
            )
            for p in self.positions(instrument=instrument)
            if p.size != 0
        ]
        return await asyncio.gather(*(self.newOrder(order) for order in orders))


setattr(Strategy.onTrade, "_original", 1)
setattr(Strategy.onOrder, "_original", 1)
setattr(Strategy.onOpen, "_original", 1)
setattr(Strategy.onCancel, "_original", 1)
setattr(Strategy.onChange, "_original", 1)
setattr(Strategy.onFill, "_original", 1)
setattr(Strategy.onData, "_original", 1)
setattr(Strategy.onHalt, "_original", 1)
setattr(Strategy.onContinue, "_original", 1)
setattr(Strategy.onError, "_original", 1)
setattr(Strategy.onStart, "_original", 1)
setattr(Strategy.onExit, "_original", 1)

setattr(Strategy.onBought, "_original", 1)
setattr(Strategy.onSold, "_original", 1)
setattr(Strategy.onRejected, "_original", 1)
setattr(Strategy.onTraded, "_original", 1)
