import asyncio
from datetime import datetime, timedelta
import inspect
import os
import os.path

from typing import (
    Any,
    Awaitable,
    AsyncGenerator,
    Callable,
    Dict,
    List as ListType,
    Optional,
    Tuple,
)

from aiostream.stream import merge  # type: ignore

from mxts.core.handler import EventHandler, PrintHandler
from mxts.data.data import Event, Error
from mxts.config import TradingType, EventType, getStrategies, getExchanges
from mxts.exchange import Exchange
from mxts.strategy import Strategy

from .managers import StrategyManager, OrderManager, PortfolioManager, RiskManager

try:
    import uvloop  # type: ignore
except ImportError:
    uvloop = None


class TradingEngine(object):
    """Main trading application
    
    """

    def __init__(self, **config: dict) -> None:

        # run in verbose mode (print all events)
        self.verbose = config["verbose"]

        # Trading type
        self.trading_type = config["trading_type"]

        # Engine heartbeat interval in seconds 
        self.heartbeat = config["heartbeat"]

        # Load account information from exchanges
        self.load_accounts = config["load_accounts"]

        # Load exchange instances
        self.exchanges = get_exchanges(
            config["exchanges"],
            trading_type=self.trading_type,
            verbose=self.verbose,
        )

        # instantiate the Strategy Manager
        self.manager = StrategyManager(
            self, self.trading_type, self.exchanges, self.load_accounts
        )

        # set event loop to use uvloop
        if uvloop:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        # install event loop
        self.event_loop = asyncio.get_event_loop()

        # setup subscriptions
        self._handler_subscriptions: Dict[EventType, List] = {
            m: [] for m in EventType.__members__.values()
        }

        # setup `now` handler for backtest
        self._latest = datetime.fromtimestamp(0) if self.offline else datetime.now()

        # register internal management event handler before all strategy handlers
        self.registerHandler(self.manager)

        # install event handlers
        self.strategies = get_strategies(config["strategy"])

        for strategy in self.strategies:
            self.log.critical(f"Installing strategy: {strategy}")
            self.registerHandler(strategy)

        # warn if no event handlers installed
        if not self.event_handlers:
            self.log.critical("Warning! No event handlers set")

        # install print handler if verbose
        if self.verbose:
            self.log.critical("Installing print handler")
            self.registerHandler(PrintHandler())

    @property
    def offline(self) -> bool:
        return self.trading_type in (TradingType.BACKTEST, TradingType.SIMULATION)

    def registerHandler(self, handler: EventHandler) -> Optional[EventHandler]:
        """register a handler and all callbacks that handler implements
        Args:
            handler (EventHandler): the event handler to register
        Returns:
            value (EventHandler or None): event handler if its new, else None
        """
        if handler not in self.event_handlers:
            # append to handler list
            self.event_handlers.append(handler)

            # register callbacks for event types
            for type in EventType.__members__.values():
                # get callback or callback tuple
                # could be none if not implemented
                cbs = handler.callback(type)

                for cb in cbs:
                    if cb:
                        self.registerCallback(type, cb, handler)
            handler._setManager(self.manager)
            return handler
        return None

    # def _make_async(self, function: Callable) -> Callable[..., Awaitable]:
    #    async def _wrapper(event: Event) -> Any:
    #        return await self.event_loop.run_in_executor(self.executor, function, event)
    #
    #    return _wrapper

    

    def registerCallback(
        self, event_type: EventType, callback: Callable, handler: EventHandler = None
    ) -> bool:
        """register a callback for a given event type
        Args:
            event_type (EventType): event type enum value to register
            callback (function): function to call on events of `event_type`
            handler (EventHandler): class holding the callback (optional)
        Returns:
            value (bool): True if registered (new), else False
        """
        if (callback, handler) not in self._handler_subscriptions[event_type]:
            if not asyncio.iscoroutinefunction(callback):
                callback = self._make_async(callback)
            self._handler_subscriptions[event_type].append((callback, handler))
            return True
        return False

    def pushEvent(self, event: Event) -> None:
        """push non-exchange event into the queue"""
        self._queued_events.append(event)

    def pushTargetedEvent(self, strategy: Strategy, event: Event) -> None:
        """push non-exchange event targeted to a specific strat into the queue"""
        self._queued_targeted_events.append((strategy, event))

    async def run(self) -> None:
        """run the engine"""
        # setup future queue
        self._queued_events: Deque[Event] = asyncio.Queue()
        self._queued_targeted_events: Deque[Tuple[Strategy, Event]] = asyncio.Queue()

        # await all connections
        await asyncio.gather(
            *(asyncio.create_task(exch.connect()) for exch in self.exchanges)
        )
        await asyncio.gather(
            *(asyncio.create_task(exch.instruments()) for exch in self.exchanges)
        )

        # send start event to all callbacks
        await self.processEvent(Event(type=EventType.START, target=None))

        # **************** #
        # Main event loop
        # **************** #
        async with merge(
            *(
                exch.tick()
                for exch in self.exchanges + [self]
                if inspect.isasyncgenfunction(exch.tick)
            )
        ).stream() as stream:
            # stream through all events
            async for event in stream:
                
                # tick exchange event to handlers
                await self.processEvent(event)

                self._latest = datetime.now()

                # process any secondary events
                while self._queued_events:
                    event = self._queued_events.popleft()
                    await self.processEvent(event)

                # process any secondary callback-targeted events (e.g. order fills)
                # these need to route to a specific callback,
                # rather than all callbacks
                while self._queued_targeted_events:
                    strat, event = self._queued_targeted_events.popleft()

                    # send to the generating strategy
                    await self.processEvent(event, strat)

                # process any periodics
                # periodic_result = await asyncio.gather(
                #     *(
                #         asyncio.create_task(p.execute(self._latest))
                #         for p in self.manager.periodics()
                #s         if p.expires(self._latest)
                #     )
                # )

                # exceptions = [r for r in periodic_result if r.exception()]
                #if any(exceptions):
                #    raise exceptions[0].exception()

        # Before engine shutdown, send an exit event
        await self.processEvent(Event(type=EventType.EXIT, target=None))

    async def processEvent(self, event: Event, strategy: Strategy = None) -> None:
        """send an event to all registered event handlers
        Arguments:
            event (Event): event to send
        """
        if event.type == EventType.HEARTBEAT:
            # ignore heartbeat
            return

        for callback, handler in self._handler_subscriptions[event.type]:
            # TODO make cleaner? move to somewhere not in critical path?
            if strategy is not None and (handler not in (strategy, self.manager)):
                continue

            # TODO make cleaner? move to somewhere not in critical path?
            if (
                event.type
                in (
                    EventType.TRADE,
                    EventType.OPEN,
                    EventType.CHANGE,
                    EventType.CANCEL,
                    EventType.DATA,
                )
                and not self.manager.dataSubscriptions(handler, event)
            ):
                continue

            try:
                await callback(event)
            except KeyboardInterrupt:
                raise
            except SystemExit:
                raise
            except BaseException as e:
                if event.type == EventType.ERROR:
                    # don't infinite error
                    raise
                await self.processEvent(
                    Event(
                        type=EventType.ERROR,
                        target=Error(
                            target=event,
                            handler=handler,
                            callback=callback,
                            exception=e,
                        ),
                    )
                )
                await asyncio.sleep(1)

    async def tick(self) -> AsyncGenerator:
        """helper method execute periodically in absenceof market data"""

        if self.offline:
            # periodics injected manually, see main event loop above
            return

        while True:
            yield Event(type=EventType.HEARTBEAT, target=None)
            await asyncio.sleep(self.heartbeat)

    def now(self) -> datetime:
        """Return the current datetime. Useful to avoid code changes between
        live trading and backtesting. Defaults to `datetime.now`"""
        return (
            self._latest
            if self.trading_type == TradingType.BACKTEST
            else datetime.now()
        )

    def start(self) -> None:
        try:
            self.event_loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            pass

        # send exit event to all callbacks
        asyncio.ensure_future(
            self.processEvent(Event(type=EventType.EXIT, target=None))
        )