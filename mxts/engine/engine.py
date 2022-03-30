import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import inspect
from typing import (
    Any,
    Awaitable,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)

from aiostream.stream import merge  # type: ignore

from mxts.core.handler import EventHandler
from mxts.data import Event, Error
from mxts.config import TradingType, EventType
from mxts.config.config import Settings
from mxts.exchange import Exchange
from mxts.exchange.coinbase.coinbase import CoinbaseProExchange
from mxts.strategy import Strategy

from .managers import StrategyManager, OrderManager, PortfolioManagers, RiskManager

try:
    import uvloop  # type: ignore
except ImportError:
    uvloop = None


class TradingEngine(object):
    """Main trading application
    
    """

    def __init__(self, config: Settings) -> None:

        # run in verbose mode (print all events)
        self.verbose = config.verbose

        # Trading type
        self.trading_type = config.trading_type

        # Engine heartbeat interval in seconds 
        self.heartbeat = config.heartbeat

        # Load account information from exchanges
        self.load_accounts = config.load_accounts

        # TODO replace with Ray
        self.executer = ThreadPoolExecutor()
        
        # Load exchange instances
        #self.exchanges = get_exchanges(
        #    config["exchanges"],
        #    trading_type=self.trading_type,
        #    verbose=self.verbose,
        #)

        # TODO: configure exchange in Settings Object
        self.exchanges = [CoinbaseProExchange()]
        
        # instantiate the Strategy Manager
        self.strat_mgr = StrategyManager(
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
        self.register_handler(self.strat_mgr)

        # install event handlers
        # self.strategies = get_strategies(config["strategy"])
        
        self.strategies = ()

        self.event_handlers = ()
        
        for strategy in self.strategies:
            self.log.critical(f"Installing strategy: {strategy}")
            self.register_handler(strategy)

        # warn if no event handlers installed
        if not self.event_handlers:
            self.log.critical("Warning! No event handlers set")

        # install print handler if verbose
        if self.verbose:
            self.log.critical("Installing print handler")
            # self.register_handler(PrintHandler())

    @property
    def offline(self) -> bool:
        return self.trading_type in (TradingType.BACKTEST, TradingType.SIMULATION)

    def register_handler(self, handler: EventHandler) -> Optional[EventHandler]:
        """register a handler and all callbacks that handler implements
        Args:
            handler (EventHandler): the event handler to register
        Returns:
            value (EventHandler or None): event handler if its new, else None
        """
        # TODO: check if this is necessary, probably not
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
                        self.register_callback(type, cb, handler)
            handler._set_manager(self.strat_mgr)
            return handler
        return None

    # def _make_async(self, function: Callable) -> Callable[..., Awaitable]:
    #    async def _wrapper(event: Event) -> Any:
    #        return await self.event_loop.run_in_executor(self.executor, function, event)
    #
    #    return _wrapper

    def register_callback(
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
            # if not asyncio.iscoroutinefunction(callback):
            #     callback = self._make_async(callback)
            self._handler_subscriptions[event_type].append((callback, handler))
            return True
        return False

    async def push_event(self, event: Event) -> None:
        """push non-exchange event into the queue"""
        await self._event_queue.put(event)

    async def run(self) -> None:
        """run the engine"""
        # setup future queue
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        
        # self._queued_targeted_events: Deque[Tuple[Strategy, Event]] = asyncio.Queue()

        # await all connections
        await asyncio.gather(
            *(asyncio.create_task(exch.connect()) for exch in self.exchanges)
        )
        await asyncio.gather(
            *(asyncio.create_task(exch.instruments()) for exch in self.exchanges)
        )

        # send start event to all callbacks
        await self.process_event(Event(type=EventType.START, target=None))

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
                await self.process_event(event)

                self._latest = datetime.now()

                # process any secondary events
                while not self._event_queue.empty():
                   
                    event = await self._event_queue.get()
                    await self.process_event(event)

                # process any secondary callback-targeted events (e.g. order fills)
                # these need to route to a specific callback,
                # rather than all callbacks
                #while self._queued_targeted_events:
                #    strat, event = self._queued_targeted_events.popleft()
                #    
                #    # send to the generating strategy
                #    await self.process_event(event, strat)

                # process any periodics
                # periodic_result = await asyncio.gather(
                #     *(
                #         asyncio.create_task(p.execute(self._latest))
                #         for p in self.strat_mgr.periodics()
                #s         if p.expires(self._latest)
                #     )
                # )

                # exceptions = [r for r in periodic_result if r.exception()]
                #if any(exceptions):
                #    raise exceptions[0].exception()

        # Before engine shutdown, send an exit event
        await self.process_event(Event(type=EventType.EXIT, target=None))

    async def process_event(self, event: Event, strategy: Strategy = None) -> None:
        """send an event to all registered event handlers
        Args:
            event (Event): event to send
            strategy (Strategy)
        """
        if event.type == EventType.HEARTBEAT:
            # ignore heartbeat
            return

        for callback, handler in self._handler_subscriptions[event.type]:
            # TODO make cleaner? move to somewhere not in critical path?
            if strategy is not None and (handler not in (strategy, self.strat_mgr)):
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
                and not self.strat_mgr.data_subscriptions(handler, event)
            ):
                continue

            try:
                # await callback(event)
                await self.event_loop.run_in_executor(self.executor, callback, event)
            except KeyboardInterrupt:
                raise
            except SystemExit:
                raise
            except BaseException as e:
                if event.type == EventType.ERROR:
                    # don't infinite error
                    raise
                await self.process_event(
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
                await asyncio.sleep(1) # TODO factor this term out

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
            self.process_event(Event(type=EventType.EXIT, target=None))
        )