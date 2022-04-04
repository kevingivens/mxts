from typing import List, TYPE_CHECKING

from mxts.core import Instrument, ExchangeType, Event, Order, Trade
from mxts.config import Side
from mxts.exchange import Exchange

from .execution import OrderManager
from .portfolio import PortfolioManager
from .risk import RiskManager

if TYPE_CHECKING:
    from mxts.engine import TradingEngine
    from mxts.strategy import Strategy


class StratMgrOrderEntryMixin(object):
    _engine: "TradingEngine"
    _exchanges: List[Exchange]
    _trades: dict
    _open_orders: dict
    _closed_orders: dict
    _alerted_events: dict
    _risk_mgr: RiskManager
    _order_mgr: OrderManager
    _portfolio_mgr: PortfolioManager

    #####################
    # Order Entry Hooks #
    #####################
    
    # TODO fix ugly private method
    async def _on_bought(self, strategy: "Strategy", trade: Trade) -> None:
        # append to list of trades
        self._trades[strategy].append(trade)

        # push event to loop
        ev = Event(type=Event.Types.BOUGHT, target=trade)
        self._engine.push_targeted_event(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, trade.my_order)

    async def _on_sold(self, strategy: "Strategy", trade: Trade) -> None:
        # append to list of trades
        self._trades[strategy].append(trade)

        # push event to loop
        ev = Event(type=Event.Types.SOLD, target=trade)
        self._engine.push_targeted_event(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, trade.my_order)

    # TODO ugly private method

    async def _on_received(self, strategy: "Strategy", order: Order) -> None:
        # push event to loop
        ev = Event(type=Event.Types.RECEIVED, target=order)
        self._engine.push_targeted_event(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, order)

    async def _on_canceled(self, strategy: "Strategy", order: Order) -> None:
        # push event to loop
        ev = Event(type=Event.Types.CANCELED, target=order)
        self._engine.push_targeted_event(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, order)

    async def _on_rejected(self, strategy: "Strategy", order: Order) -> None:
        # push event to loop
        ev = Event(type=Event.Types.REJECTED, target=order)
        self._engine.push_targeted_event(strategy, ev)

    # *********************
    # Order Entry Methods *
    # *********************

    async def new_order(self, strategy: "Strategy", order: Order) -> bool:
        """helper method, defers to buy/sell"""
        # ensure has list
        if strategy not in self._open_orders:
            self._open_orders[strategy] = []

        if strategy not in self._closed_orders:
            self._closed_orders[strategy] = []

        if strategy not in self._trades:
            self._trades[strategy] = []

        # append to open orders list
        self._open_orders[strategy].append(order)

        # append to past orders list
        self._closed_orders[strategy].append(order)

        # TODO check risk
        order, approved = await self._risk_mgr.new_order(strategy, order)

        # was this trade allowed?
        if approved:
            # send to be executed
            received = await self._order_mgr.new_order(strategy, order)

            if received:
                await self._on_received(strategy, order)
            return received

        # raise onRejected
        await self._on_rejected(strategy, order)
        return False

    async def cancel_order(self, strategy: "Strategy", order: Order) -> bool:
        """cancel an open order"""
        ret = await self._order_mgr.cancel_order(strategy, order)
        if ret:
            await self._on_canceled(strategy, order)
            return ret

        # TODO something else?
        await self._onRejected(strategy, order)
        return False

    def orders(
        self,
        strategy: "Strategy",
        instrument: Instrument = None,
        exchange: ExchangeType = None,
        side: Side = None,
    ) -> List[Order]:
        """select all open orders

        Args:
            instrument (Instrument): filter open orders by instrument
            exchange (ExchangeType): filter open orders by exchange
            side (Side): filter open orders by side
        Returns:
            list (Order): list of open orders
        """
        # ensure has list
        if strategy not in self._open_orders:
            self._open_orders[strategy] = []

        ret = self._open_orders[strategy].copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    def past_orders(
        self,
        strategy: "Strategy",
        instrument: Instrument = None,
        exchange: ExchangeType = None,
        side: Side = None,
    ) -> List[Order]:
        """select all past orders

        Args:
            instrument (Instrument): filter open orders by instrument
            exchange (ExchangeType): filter open orders by exchange
            side (Side): filter open orders by side
        Returns:
            list (Order): list of open orders
        """
        # ensure has list
        if strategy not in self._closed_orders:
            self._closed_orders[strategy] = []

        ret = self._closed_orders[strategy].copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    def trades(
        self,
        strategy: "Strategy",
        instrument: Instrument = None,
        exchange: ExchangeType = None,
        side: Side = None,
    ) -> List[Trade]:
        """select all past trades

        Args:
            instrument (Instrument): filter trades by instrument
            exchange (ExchangeType): filter trades by exchange
            side (Side): filter trades by side
        Returns:
            list (Trade): list of trades
        """
        # ensure has list
        if strategy not in self._trades:
            self._trades[strategy] = []

        ret = self._trades[strategy].copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    #########################
    # Order Entry Callbacks #
    #########################
    async def on_traded(self, event: Event) -> None:
        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # remove from list of open orders if done
            if order.filled >= order.volume:
                try:
                    self._open_orders[strategy].remove(order)
                except ValueError:
                    ...
        else:
            strategy = None

        await self._portfolio_mgr.on_traded(event, strategy)
        await self._risk_mgr.on_traded(event, strategy)
        await self._order_mgr.on_traded(event, strategy)

    async def on_received(self, event: Event) -> None:
        # synchronize state
        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # don't remove or do anything else
        else:
            strategy = None

        await self._portfolio_mgr.on_received(event, strategy)
        await self._risk_mgr.on_received(event, strategy)
        await self._order_mgr.on_received(event, strategy)

    async def on_rejected(self, event: Event) -> None:
        # synchronize state
        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # remove from list of open orders
            try:
                self._open_orders[strategy].remove(order)
            except ValueError:
                ...
        else:
            strategy = None

        await self._portfolio_mgr.on_rejected(event, strategy)
        await self._risk_mgr.on_rejected(event, strategy)
        await self._order_mgr.on_rejected(event, strategy)

    async def on_canceled(self, event: Event) -> None:
        # synchronize state
        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # remove from list of open orders
            try:
                self._open_orders[strategy].remove(order)
            except ValueError:
                ...
        else:
            strategy = None

        await self._portfolio_mgr.on_canceled(event, strategy)
        await self._risk_mgr.on_canceled(event, strategy)
        await self._order_mgr.on_canceled(event, strategy)
