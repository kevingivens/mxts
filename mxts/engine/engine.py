import asyncio
from asyncio.log import logger
import logging
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from typing import (
    Any,
    AsyncGenerator,
    Coroutine,
    Dict,
    List,
)

from aiostream.stream import merge  # type: ignore
from cryptofeed import FeedHandler
from cryptofeed.defines import TICKER
from cryptofeed.exchanges import Coinbase, Bitfinex

from pandas import Timestamp

from mxts.core.handler import EventHandler
from mxts.core.data import Event, Error
from mxts.config import TradingType, EventType
from mxts.config.config import Settings

# from mxts.strategy import Strategy

from .managers import StrategyManager

# Set up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ticker(t, receipt_timestamp):
    print(f'Ticker received at {receipt_timestamp}: {t}')


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

        self.feed_handler = FeedHandler()

        ticker_cb = {TICKER: ticker}
        
        self.feed_handler.add_feed(
            Coinbase(symbols=['BTC-USD', 'ETH-USD'], channels=[TICKER], callbacks=ticker_cb),
            # Bitfinex(symbols=['BTC-USD'], channels=[TICKER], callbacks=ticker_cb)
        )
  
        # instantiate the Strategy Manager
        #self.strat_mgr = StrategyManager(
        #    self, self.trading_type, self.exchanges, self.load_accounts
        #)

        # set up logging, TODO: replace/consider async logger
        #self.logger = logging.getLogger(__name__)
        #if self.verbose:
        #    self.logger.setLevel(logging.DEBUG)

        # setup handler subscriptions
        # self._handler_subs: Dict[EventType, List[Coroutine]] = {
        #     e: [] for e in EventType
        # }

        # setup `now` handler for backtest
        # self._latest = Timestamp(0) if self.offline else Timestamp.now()

        # register internal management event handler before all strategy handlers
        # self.register_handler(self.strat_mgr)

        # install event handlers
        # self.strategies = get_strategies(config.strategy)
        
        self.strategies = []

        self.event_handlers = []

        # self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        
        # for strat in self.strategies:
        #    self.logger.critical(f"Installing strategy: {strat}")
        #    self.register_handler(strat)

        # warn if no event handlers installed
        # if not self.event_handlers:
        #    self.logger.critical("Warning! No event handlers set")

        # install print handler if verbose
        #if self.verbose:
        #    self.logger.critical("Installing print handler")
        #    # self.register_handler(PrintHandler())
    
    @property
    def offline(self) -> bool:
        return self.trading_type in (TradingType.BACKTEST, TradingType.SIMULATION)

    def register_handler(self, handler: EventHandler) -> None:
        """register a handler and all callbacks that handler implements
        Args:
            handler (EventHandler): the event handler to register
       
        """
        self.logger.info("registering handlers")
        if handler not in set(self.event_handlers):
            self.event_handlers.append(handler)
            for callback, events in handler.callbacks.items():
                for e in events:
                    self._handler_subs[e].append(callback)

    async def push_event(self, event: Event) -> None:
        """push internal event onto the queue"""
        await self._event_queue.put(event)

    def run(self) -> None:
        self.feed_handler.run()

    async def run_old(self) -> None:
        """main event loop"""
        async with merge(
            *(ex.tick() for ex in self.exchanges + [self])
        ).stream() as stream:
            # stream through all events
            async for event in stream:
                
                # tick exchange event to handlers
                await self.process_event(event)

                self._latest = Timestamp.now()

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
        self.logger.info(f"processing event: {event}")
        if event.type == EventType.HEARTBEAT:
            # ignore heartbeat
            return

        for callback in self._handler_subs[event.type]:
            # TODO make cleaner? move to somewhere not in critical path?
            # if strategy is not None and (handler not in (strategy, self.strat_mgr)):
            #    continue
            # TODO make cleaner? move to somewhere not in critical path?
            #if (
            #    event.type
            #    in (
            #        EventType.TRADE,
            #        EventType.OPEN,
            #        EventType.CHANGE,
            #        EventType.CANCEL,
            #        EventType.DATA,
            #    )
            #    and not self.strat_mgr.data_subscriptions(handler, event)
            #):
            #    continue
            try:
                # TODO: replace thread pool with Ray
                await self.event_loop.run_in_executor(self.executor, callback, event)
            except KeyboardInterrupt:
                raise
            except SystemExit:
                raise
            except BaseException as e:
                if event.type == EventType.ERROR:
                    # avoid infinite error loop
                    raise
                await self.process_event(
                    Event(
                        type=EventType.ERROR,
                        data=Error(
                            data=event,
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

    def now(self) -> Timestamp:
        """Return the current datetime. Useful to avoid code changes between
        live trading and backtesting. Defaults to `Timestamp.now`"""
        return (
            self._latest
            if self.trading_type == TradingType.BACKTEST
            else Timestamp.now()
        )

    def start(self) -> None:
        # TODO replace this with trading session context manager
        try:
            self.event_loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            pass

        # send exit event to all callbacks
        asyncio.ensure_future(
            self.process_event(Event(type=EventType.EXIT, data=None))
        )
    
    async def startup(self):
        # START UP TASKS:
        # Engine: connect to all clients 
        # Exchange: check available instruments 
        # Exchange: check balances, then aggregate 
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
        # Exchange: Collect closing balances
        # Engine: Disconnect from exchanges
        # Engine: Write info to disk
        # Close DB connections
        # Before engine shutdown, send an exit event
        # await self.process_event(Event(type=EventType.EXIT, target=None))
        pass