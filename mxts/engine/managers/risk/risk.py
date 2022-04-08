from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from mxts.config import ExitRoutine
from mxts.core.data import Event, Order, Trade, Position
from mxts.core.handler import EventHandler

from ..base import ManagerBase


if TYPE_CHECKING:
    from mxts.strategy import Strategy
    from ..strategy import StrategyManager


class RiskManager(ManagerBase):
    def __init__(self) -> None:
        # Track active (open) orders
        self._active_orders: List[Order] = []

        # Restricted hours
        self._restricted_trading_hours: Dict["Strategy", Tuple[int, ...]] = {}

    def update_account(self, positions: List[Position]) -> None:
        """update positions tracking with a position from the exchange"""
        pass

    def update_cash(self, positions: List[Position]) -> None:
        """update cash positions from exchange"""
        pass

    def restrict_trading_hours(
        self,
        strategy: "Strategy",
        start_second: Optional[int] = None,
        start_minute: Optional[int] = None,
        start_hour: Optional[int] = None,
        end_second: Optional[int] = None,
        end_minute: Optional[int] = None,
        end_hour: Optional[int] = None,
        on_end_of_day: ExitRoutine = ExitRoutine.NONE,
    ) -> None:
        pass

    # *********************
    # Risk Methods        *
    # *********************
    def risk(self, position: Position = None) -> str:  # TODO
        # TODO
        return "risk"

    # *********************
    # Order Entry Methods *
    # *********************
    async def new_order(self, strategy: "Strategy", order: Order) -> Tuple[Order, bool]:
        # TODO
        self._active_orders.append(order)  # TODO use strategy
        return order, True

    # **********************
    # EventHandler methods *
    # **********************
    async def on_trade(self, event: Event) -> None:
        # TODO
        pass

    async def on_cancel(self, event: Event) -> None:
        # TODO
        pass

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
        trade: Trade = event.target  # type: ignore

        if (
            trade.my_order in self._active_orders
            and trade.my_order.filled >= trade.my_order.volume
        ):
            self._active_orders.remove(trade.my_order)

    async def on_received(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def on_rejected(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        order: Order = event.target  # type: ignore

        if order in self._active_orders:
            self._active_orders.remove(order)

    async def on_canceled(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        order: Order = event.target  # type: ignore

        if order in self._active_orders:
            self._active_orders.remove(order)
