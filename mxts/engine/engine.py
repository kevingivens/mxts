import asyncio
import datetime
import logging
from typing import AsyncGenerator
   
# from aiostream.stream import merge  # type: ignore
from cryptofeed import FeedHandler
from cryptofeed.defines import TICKER
from cryptofeed.exchanges import EXCHANGE_MAP

from pandas import Timestamp

from mxts.core.handler import EventHandler
from mxts.core.data import Event
from mxts.config import TradingType, EventType
from mxts.config.config import Settings
from mxts.engine.portfolio import dump, load

LOG = logging.getLogger('mxts')

# async def ticker(t, receipt_timestamp):
#     print(f'Ticker received at {receipt_timestamp}: {t}')

async def ticker(obj, receipt_ts):
    # For debugging purposes
    rts = datetime.utcfromtimestamp(receipt_ts).strftime('%Y-%m-%d %H:%M:%S')
    print(f"{rts} - {obj}")


class TradingEngine:
    """ Main trading application
    """
    def __init__(self, config: Settings) -> None:

        self.config = config
        
        # exchange connections
        self.feeds = {}
        
        for exch in self.config.exchanges:
            self.feeds[exch] = EXCHANGE_MAP[exch](
                    sandbox=self.config.trading_type == TradingType.SANDBOX,
                    symbols=self.config.symbols, 
                    channels=[TICKER], 
                    callbacks={TICKER: ticker}
                )

        # feeds are added in the run method
        self.feed_handler = FeedHandler()
            
        self.portfolio = load(config.portfolio_fp)
        LOG.info(f"loaded a portfolio with balance: {self.portfolio.balance}")
        
        self.alpha_models = []

    
    @property
    def offline(self) -> bool:
        return self.config.trading_type in (TradingType.BACKTEST, TradingType.SIMULATION)

    def register_handler(self, handler: EventHandler) -> None:
        """register a handler and all callbacks that handler implements
        Args:
            handler (EventHandler): the event handler to register
       
        """
        LOG.info("registering handlers")
        if handler not in set(self.event_handlers):
            self.event_handlers.append(handler)
            for callback, events in handler.callbacks.items():
                for e in events:
                    self._handler_subs[e].append(callback)

    async def push_event(self, event: Event) -> None:
        """push internal event onto the queue"""
        await self._event_queue.put(event)

    def run(self) -> None:
        # register the feeds
        for exch in self.feeds.values():
            self.feed_handler.add_feed(exch)
    
        self.feed_handler.run()

    async def tick(self) -> AsyncGenerator:
        """helper method execute periodically in absence of market data"""

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

    def startup(self):
        # TODO: replace startup and shutdown with a context mgr
        # check symbols 
        for k, v in self.feeds.items():
            for sym in self.config.symbols:
                if sym not in v.symbols:
                    LOG.warn("sym {sym} in not in {k} exchange")
        
        # get balances
        balances = {}
        for k, v in self.feeds.items():
            balances[k] = v.sync_balances()

    async def shutdown(self):
        # SHUTDOWN TASKS:
        # Exchange: Collect closing balances
        # Engine: Disconnect from exchanges
        # Engine: Write info to disk
        # Close DB connections
        # Before engine shutdown, send an exit event
        # await self.process_event(Event(type=EventType.EXIT, target=None))
        pass