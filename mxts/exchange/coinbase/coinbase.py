import os
from typing import List, AsyncGenerator, Any

from mxts.core import ExchangeType, Order, Instrument, Position, Event
from mxts.config import TradingType, InstrumentType


from yarl import URL

#from mxts.exchange import Exchange

from .client import CoinbaseClient



#class CoinbaseProExchange(Exchange):

class CoinbaseProExchange():
    """Coinbase Pro Exchange
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
        api_passphrase: str = "",
        **kwargs: dict
    ) -> None:
        self._trading_type = trading_type
        self._verbose = verbose

        base_urls = {
            TradingType.SANDBOX: URL("https://api-public.sandbox.exchange.coinbase.com"),
            TradingType.LIVE: URL("https://api.exchange.coinbase.com")
        }

        # coinbase keys
        self._api_key = api_key
        self._api_secret = api_secret
        self._api_passphrase = api_passphrase

        # Create an exchange client based on the coinbase docs
        # Note: cbpro doesnt seem to work as well as I remember,
        # and ccxt has moved to a "freemium" model where coinbase
        # pro now costs money for full access, so here i will just
        # implement the api myself.
        self._client = CoinbaseClient(
            base_urls[self._trading_type],
            # self.exchange(),
            self._api_key,
            self._api_secret,
            self._api_passphrase,
        )

        # list of market data subscriptions
        # self._subscriptions: List[Instrument] = []
        self._subscriptions = ['BTC-USD']
    
     async def tick(self) -> AsyncGenerator[Any, Event]:  # type: ignore[override]
         async with self._client as client:
             while True:
                ticker = await self._client.get_ticker(self._subscriptions)
                yield ticker
