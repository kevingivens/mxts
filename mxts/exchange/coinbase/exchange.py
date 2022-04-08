from typing import List, AsyncGenerator, Any

# from mxts.core import ExchangeType, Order, Instrument, Position, Event
# from mxts.config import TradingType, InstrumentType

from mxts.core.data import Event, Instrument
from mxts.config import TradingType

from yarl import URL

# from mxts.exchange import Exchange
from .client import CoinbaseClient


class CoinbaseProExchange():
    """Coinbase Pro Exchange
    
        TODO: inherit from Exchange base class to e
    Args:
        trading_type (TradingType): type of trading to do. Must be Sandbox or Live
        verbose (bool): run in verbose mode
        api_key (str): Coinbase API key
        api_secret (str): Coinbase API secret
        api_passphrase (str): Coinbase API passphrase
        order_book_level (str): Level of orderbook to trace, must be 'l3', 'l2', or 'trades'
    """

    def __init__(
        self,
        verbose= False,
        trading_type= TradingType.SANDBOX,
        api_key: str = "",
        api_secret: str = "",
        api_passphrase: str = ""
    ) -> None:
        self._trading_type = trading_type
        self._verbose = verbose

        base_urls = {
            TradingType.SANDBOX: URL("https://api-public.sandbox.exchange.coinbase.com"),
            TradingType.LIVE: URL("https://api.exchange.coinbase.com")
        }

        # Create an exchange client
        self._client = CoinbaseClient(
            base_urls[self._trading_type],
            # self.exchange(),
            api_key,
            api_secret,
            api_passphrase,
        )

        # list of market data subscriptions
        # self._subscriptions: List[Instrument] = []
        self._subscriptions = ['BTC-USD']
    
    async def tick(self) -> AsyncGenerator[Any, Event]:  # type: ignore[override]
        async with self._client as client:
            while True:
               ticker = await self._client.get_ticker(self._subscriptions)
               yield ticker
    
    async def instruments(self) -> List[Instrument]:  # type: ignore[override]
        async with self._client as client:
            ret = await self._client.get_currencies()

