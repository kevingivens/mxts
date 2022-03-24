import sys
import traceback

from typing import cast, List, TYPE_CHECKING

from .order_entry import StrategyManagerOrderEntryMixin, OrderManager
# from .periodic import PeriodicManagerMixin
from .portfolio import StrategyManagerPortfolioMixin, PortfolioManager
# from .risk import StrategyManagerRiskMixin, RiskManager
from .utils import StrategyManagerUtilsMixin

from mxts.config import TradingType
from mxts.core import Event, Error
from mxts.exchange import Exchange
from mxts.core.handler import EventHandler


if TYPE_CHECKING:
    from mxts.strategy import Strategy
    from mxts.engine import TradingEngine

# TODO: rename file strat_mgr

class StrategyManager(
    StrategyManagerOrderEntryMixin,
    # StrategyManagerRiskMixin,
    StrategyManagerPortfolioMixin,
    StrategyManagerUtilsMixin,
    # PeriodicManagerMixin,
    EventHandler,
):
    def __init__(
        self,
        trading_engine: "TradingEngine",
        trading_type: TradingType,
        exchanges: List[Exchange],
        load_accounts: bool = False,
    ) -> None:
        """The Manager sits between the strategies and the engine and manages state

        Args:
            trading_engine (TradingEngine); the trading engine instance
            trading_type (TradingType); the trading type
            exchanges (List[Exchange]); a list of exchanges to dispatch to
            load_accounts (bool); load positions from accounts on startup
        """

        # store trading engine
        self._engine = trading_engine

        # store the exchanges
        self._exchanges = exchanges

        # store whether to query accounts on start
        self._load_accounts = load_accounts

        # pull from trading engine class
        self._portfolio_mgr = self._engine.portfolio_manager
        # self._risk_mgr = self._engine.risk_manager
        self._order_mgr = self._engine.order_manager

        # install self for callbacks
        self._portfolio_mgr._set_manager(self)
        # self._risk_mgr._set_manager(self)
        self._order_mgr._set_manager(self)

        # add exchanges for order manager
        for exc in exchanges:
            self._order_mgr.add_exchange(exc)

        # initialize event subscriptions
        self._data_subscriptions = {}  # type: ignore

        # initialize order and trade tracking
        self._strategy_open_orders = {}
        self._strategy_past_orders = {}
        self._strategy_trades = {}

        # internal use for synchronizing
        self._alerted_events = {}

        # internal use for periodics
        self._periodics = []

    # ********* #
    # Accessors #
    # ********* #
    #@property
    #def risk_manager(self) -> RiskManager:
    #    return self._risk_mgr
    
    @property
    def order_manager(self) -> OrderManager:
        return self._order_mgr

    @property
    def portfolio_manager(self) -> PortfolioManager:
        return self._portfolio_mgr
    
    @property
    def strategies(self) -> List["Strategy"]:
        return self._engine.strategies
    
    @property
    def exchange_instances(self) -> List[Exchange]:
        return self._engine.exchanges

    # ********************* #
    # EventHandler methods *
    # **********************
    async def on_trade(self, event: Event) -> None:
        await self._portfolio_mgr.on_trade(event)
        # await self._risk_mgr.on_trade(event)
        await self._order_mgr.on_trade(event)

    async def on_open(self, event: Event) -> None:
        await self._portfolio_mgr.on_open(event)
        # await self._risk_mgr.on_open(event)
        await self._order_mgr.on_open(event)

    async def on_cancel(self, event: Event) -> None:
        await self._portfolio_mgr.on_cancel(event)
        # await self._risk_mgr.on_cancel(event)
        await self._order_mgr.on_cancel(event)

    async def on_change(self, event: Event) -> None:
        await self._portfolio_mgr.on_change(event)
        # await self._risk_mgr.on_change(event)
        await self._order_mgr.on_change(event)

    async def on_fill(self, event: Event) -> None:
        await self._portfolio_mgr.on_fill(event)
        # await self._risk_mgr.on_fill(event)
        await self._order_mgr.on_fill(event)

    async def onHalt(self, event: Event) -> None:
        await self._portfolio_mgr.on_halt(event)
        # await self._risk_mgr.on_halt(event)
        await self._order_mgr.on_halt(event)

    async def onContinue(self, event: Event) -> None:
        await self._portfolio_mgr.on_continue(event)
        # await self._risk_mgr.on_continue(event)
        await self._order_mgr.on_continue(event)

    async def on_data(self, event: Event) -> None:
        await self._portfolio_mgr.on_data(event)
        # await self._risk_mgr.on_data(event)
        await self._order_mgr.on_data(event)

    async def on_error(self, event: Event) -> None:
        print("\n\nA Fatal Error has occurred:")
        error = cast(Error, event.target)
        traceback.print_exception(
            type(error.exception),
            error.exception,
            error.exception.__traceback__,
        )
        sys.exit(1)

    async def on_exit(self, event: Event) -> None:
        await self._portfolio_mgr.on_exit(event)
        # await self._risk_mgr.on_exit(event)
        await self._order_mgr.on_exit(event)

    async def on_start(self, event: Event) -> None:
        # Initialize strategies
        self._portfolio_mgr.update_strategies(self.strategies())

        # Initialize positions
        for exch in self.exchange_instances:
            if self._load_accounts:
                acc = await exch.accounts()
                self._portfolio_mgr.update_account(acc)

            acc = await exch.balance()
            self._portfolio_mgr.update_cash(acc)
            # self._risk_mgr.update_cash(acc)

        # Defer to sub on_starts
        await self._portfolio_mgr.on_start(event)
        # await self._risk_mgr.on_start(event)
        await self._order_mgr.on_start(event)
