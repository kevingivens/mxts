import pandas as pd  # type: ignore
from datetime import datetime
from typing import cast, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

from mxts.core import Event, Trade, Instrument, ExchangeType, Position

from ..base import ManagerBase
from .portfolio import Portfolio


if TYPE_CHECKING:
    from mxts.strategy import Strategy
    from ..strategy import StrategyManager


class PortfolioManager(ManagerBase):
    def __init__(self) -> None:
        self._portfolio = Portfolio()

        # Track prices over time
        self._prices: Dict[Instrument, List[Tuple[datetime, float]]] = {}
        self._trades = {}  # type: ignore

        # Track active (open) orders
        self._active_orders = []  # type: ignore

        # Track active positions
        self._active_positions = {}  # type: ignore

    def _set_manager(self, manager: "StrategyManager") -> None:
        """install manager"""
        self._manager = manager

    def new_position(self, trade: Trade, strategy: "Strategy") -> None:
        """create and track a new position, or update the pnl/price of
        an existing position"""
        self._portfolio.new_position(trade, strategy)

    def update_strategies(self, strategies: List["Strategy"]) -> None:
        """update with list of strategies"""
        self._portfolio.update_strategies(strategies)

    def updateAccount(self, positions: List[Position]) -> None:
        """update positions tracking with a position from the exchange"""
        self._portfolio.update_account(positions)

    def updateCash(self, positions: List[Position]) -> None:
        """update cash positions from exchange"""
        self._portfolio.update_cash(positions)

    # *********************
    # Risk Methods        *
    # *********************
    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    def positions(
        self,
        strategy: "Strategy",
        instrument: Instrument = None,
        exchange: ExchangeType = None,
    ) -> List[Position]:
        return self._portfolio.positions(
            strategy=strategy, instrument=instrument, exchange=exchange
        )

    def price_history(self, instrument: Instrument = None) -> Union[dict, pd.DataFrame]:
        if instrument:
            return pd.DataFrame(
                self._prices[instrument], columns=[instrument.name, "when"]
            )
        return {
            i: pd.DataFrame(self._prices[i], columns=[i.name, "when"])
            for i in self._prices
        }

    # **********************
    # EventHandler methods *
    # **********************
    async def on_trade(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        self._portfolio.on_trade(trade)

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
        self, event: Event, strategy: Optional["Strategy"]
    ) -> None:
        self._portfolio.on_traded(cast(Trade, event.target), cast("Strategy", strategy))
