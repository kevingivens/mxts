from typing import TYPE_CHECKING, cast, Dict, List, Optional, Tuple

from mxts.core import Order, Event, Trade, ExchangeType
from mxts.core.handler import EventHandler
from mxts.exchange import Exchange
from ..base import ManagerBase


if TYPE_CHECKING:
    from mxts.strategy import Strategy
    from ..manager import StrategyManager


class OrderManager(ManagerBase):
    def __init__(self) -> None:
        # map exchangetype to exchange instance
        self._exchanges: Dict[ExchangeType, Exchange] = {}

        # track which strategies generated which orders
        self._pending_orders: Dict[str, Tuple[Order, Optional["Strategy"]]] = {}

        # past orders
        self._past_orders: List[Order] = []

    def add_exchange(self, exchange: Exchange) -> None:
        """add an exchange"""
        self._exchanges[exchange.exchange()] = exchange

    def _set_manager(self, manager: "StrategyManager") -> None:  # type: ignore
        """install manager"""
        self._manager = manager

    # *********************
    # Order Entry Methods *
    # *********************
    async def new_order(self, strategy: Optional["Strategy"], order: Order) -> bool:
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception("Exchange not installed: {}".format(order.exchange))

        ret = await exchange.newOrder(order)
        self._pending_orders[order.id] = (order, strategy)
        return ret

    async def cancel_order(self, strategy: Optional["Strategy"], order: Order) -> bool:
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception("Exchange not installed: {}".format(order.exchange))

        ret = await exchange.cancelOrder(order)
        self._pending_orders.pop(order.id, None)
        return ret

    # **********************
    # EventHandler methods *
    # **********************
    async def on_trade(self, event: Event) -> None:
        """Match trade with order"""
        action: bool = False
        strat: Optional[EventHandler] = None

        trade: Trade = event.target  # type: ignore

        for maker_order in trade.maker_orders:
            if maker_order.id in self._pending_orders:
                action = True
                order, strat = self._pending_orders[maker_order.id]

                # TODO cleaner?
                trade.my_order = order
                trade.id = order.id
                order.filled = maker_order.filled
                break

        if trade.taker_order.id in self._pending_orders:
            action = True
            order, strat = self._pending_orders[trade.taker_order.id]

            # TODO cleaner?
            trade.my_order = order
            trade.id = order.id
            order.filled = trade.taker_order.filled

        if action:
            if order.side == Order.Sides.SELL:
                # TODO ugly private method
                await self._manager._onSold(
                    cast("Strategy", strat), cast(Trade, event.target)
                )
            else:
                # TODO ugly private method
                await self._manager._onBought(
                    cast("Strategy", strat), cast(Trade, event.target)
                )

            if order.finished():
                del self._pending_orders[order.id]

    async def on_cancel(self, event: Event) -> None:
        canceled_order: Order = event.target  # type: ignore
        if canceled_order.id in self._pending_orders:
            order, strat = self._pending_orders[canceled_order.id]

            # TODO second look, just in case
            order.filled = canceled_order.filled

            # TODO ugly private method
            await self._manager._onCanceled(cast("Strategy", strat), order)
            del self._pending_orders[canceled_order.id]

    async def on_open(self, event: Event) -> None:
        # TODO
        pass

    async def on_fill(self, event: Event) -> None:
        # TODO
        pass

    async def on_change(self, event: Event) -> None:
        # TODO
        pass

    async def on_data(self, event: Event) -> None:
        # TODO
        pass

    async def on_halt(self, event: Event) -> None:
        # TODO
        pass

    async def on_continue(self, event: Event) -> None:
        # TODO
        pass

    async def on_error(self, event: Event) -> None:
        # TODO
        pass

    async def on_start(self, event: Event) -> None:
        # TODO
        pass

    async def on_exit(self, event: Event) -> None:
        # TODO
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def on_traded(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def on_received(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def on_rejected(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def on_canceled(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass
