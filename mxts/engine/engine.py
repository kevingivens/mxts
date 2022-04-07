import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import inspect
from typing import (
    Any,
    Awaitable,
    AsyncGenerator,
    Callable,
    Coroutine,
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
from mxts.exchange.coinbase.exchange import CoinbaseProExchange
# from mxts.strategy import Strategy

from .managers import StrategyManager

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

        # TODO: configure exchange in get_exchange method
        self.exchanges = []
        
        #self.exchanges = [
        #    CoinbaseProExchange(
        #        verbose = self.verbose,
        #        trading_type = self.trading_type,
        #        key = config.cb_key,
        #        secret = config.cb_secret,
        #        passphrase = config.cb_passphrase,
        #    )
        #]
        
        # instantiate the Strategy Manager
        #self.strat_mgr = StrategyManager(
        #    self, self.trading_type, self.exchanges, self.load_accounts
        #)

        # set event loop to use uvloop
        if uvloop:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        # install event loop
        self.event_loop = asyncio.get_event_loop()

        # setup handler subscriptions
        self._handler_subs: Dict[EventType, List[Coroutine]] = {
            e: [] for e in EventType
        }

        # setup `now` handler for backtest
        self._latest = datetime.fromtimestamp(0) if self.offline else datetime.now()

        # register internal management event handler before all strategy handlers
        # self.register_handler(self.strat_mgr)

        # install event handlers
        # self.strategies = get_strategies(config["strategy"])
        
        self.strategies = []

        self.event_handlers = []

        # setup future queue
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        
        for strat in self.strategies:
            self.log.critical(f"Installing strategy: {strat}")
            self.register_handler(strat)

        # warn if no event handlers installed
        if not self.event_handlers:
            self.log.critical("Warning! No event handlers set")

        # install print handler if verbose
        if self.verbose:
            self.log.critical("Installing print handler")
            # self.register_handler(PrintHandler())
    
    
    async def startup(self):
        # START UP TASKS:
        # connect to all clients 
        # check available instruments 
        # check balances 
        # log info to db? 
        # query historical data?
        # await asyncio.gather(
        #     *(asyncio.create_task(exch.connect()) for exch in self.exchanges)
        # )
        # await asyncio.gather(
        #     *(asyncio.create_task(exch.instruments()) for exch in self.exchanges)
        # )
        # send start event to all callbacks
        # await self.process_event(Event(type=EventType.START, target=None))
        pass

    
    async def shutdown(self):
        # SHUTDOWN TASKS:
        # Collect closing balances
        # Disconnect from exchanges
        # Write info to disk
        # Close DB connections
        # Before engine shutdown, send an exit event
        # await self.process_event(Event(type=EventType.EXIT, target=None))
        pass
    
    
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
            for e in EventType:
                # get callback or callback tuple
                # could be none if not implemented
                cbs = handler.callback(e)

                for cb in cbs:
                    if cb:
                        self.register_callback(e, cb, handler)
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
        
        """
        self._handler_subs[event_type].append((callback, handler))
        #if (callback, handler) not in self._handler_subs[event_type]:
        #    # if not asyncio.iscoroutinefunction(callback):
        #    #     callback = self._make_async(callback)
        #    self._handler_subs[event_type].append((callback, handler))
        #    return True
        #return False

    async def push_event(self, event: Event) -> None:
        """push non-exchange event into the queue"""
        await self._event_queue.put(event)

    async def run(self) -> None:
        """run the engine"""
        
        # self._queued_targeted_events: Deque[Tuple[Strategy, Event]] = asyncio.Queue()

        #

        # **************** #
        # Main event loop
        # **************** #
        async with merge(
            *(
                exchange.tick()
                for exchange in self.exchanges + [self]
                if inspect.isasyncgenfunction(exchange.tick)
            )
        ).stream() as stream:
            # stream through all events
            async for event in stream:
                
                # tick exchange event to handlers
                await self.process_event(event)

                self._latest = datetime.now()

                # process internal events
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

        

    async def process_event(self, event: Event) -> None:
        """send an event to all registered event handlers
        Args:
            event (Event): event to send
            strategy (Strategy)
        """
        if event.type == EventType.HEARTBEAT:
            # ignore heartbeat
            return

        for callback, handler in self._handler_subs[event.type]:
            # TODO make cleaner? move to somewhere not in critical path?
            #if strategy is not None and (handler not in (strategy, self.strat_mgr)):
            #    continue

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
                # TODO: replace thread pool with Ray
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
                await asyncio.sleep(1) # TODO make this configurable

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
        # TODO replace this with trading session context manager
        try:
            self.event_loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            pass

        # send exit event to all callbacks
        asyncio.ensure_future(
            self.process_event(Event(type=EventType.EXIT, target=None))
        )