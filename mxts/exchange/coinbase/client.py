import asyncio
import base64

import hashlib
import hmac
import time
from types import TracebackType
from typing import Any, AsyncIterator, Awaitable, Callable, List, Optional, Type

import aiohttp
from yarl import URL

from pydantic import BaseModel
from pandas import Timestamp

from .data import *
   

class _cbClient:
    def __init__(self, base_url: URL, user: str, **kwargs) -> None:
        self._base_url = base_url
        self._user = user
        self._cb_secret = kwargs.get("cb_secret")
        self._cb_key = kwargs.get("cb_key")
        self._cb_passphrase = kwargs.get("cb_passphrase")
        self._session = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._session.close()

    async def __aenter__(self) -> "_cbClient":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None
    
    def _hash_msg(self, method, url, body=""):  # type: ignore
        """This is used to sign the requests in the coinbase-specified auth scheme

        Args:
            method (_type_): _description_
            url (_type_): _description_
            body (str, optional): _description_. Defaults to "".
   
        Returns:
            _type_: _description_
        """
        timestamp = str(time.time())
        message = timestamp + method + url + body
        hmac_key = base64.b64decode(self._cb_secret)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()
   
        headers = {
           "CB-ACCESS-SIGN": signature_b64,
           "CB-ACCESS-TIMESTAMP": timestamp,
           "CB-ACCESS-KEY": self._cb_key,
           "CB-ACCESS-PASSPHRASE": self._cb_passphrase,
           "Content-Type": "application/json",
        }
       
        return headers

    def _make_url(self, path: str, params = {}) -> URL:
        return self._base_url / path % params

    
    async def get_account(self, product_id: str) -> Ticker:
        async with self._session.get(self._make_url(f"accounts")) as resp:
            ret = await resp.json()
            return Account(**ret)

    async def convert_currency(self, product_id: str) -> Ticker:
        async with self._session.post(
             self._make_url("conversions"),
             json={"owner": self._user, "title": title, "text": text},
         ) as resp:
             ret = await resp.json()


    async def get_ticker(self, product_id: str) -> Ticker:
        async with self._session.get(self._make_url(f"products/{product_id}/ticker")) as resp:
            ret = await resp.json()
            return Ticker(**ret)
    

    async def get_stats(self, product_id: str) -> Stats:
        async with self._session.get(self._make_url(f"products/{product_id}/stats")) as resp:
            ret = await resp.json()
            return Stats(**ret)
    
    async def get_candles(self, product_id: str, **kwargs) -> List[Candle]:
        """ 
            kwargs:
                granularity:  str
                start: str Timestamp for starting range of aggregations
                end: str Timestamp for ending range of aggregations
        
        """
        async with self._session.get(self._make_url(f"products/{product_id}/candles", params=kwargs)) as resp:
            ret = await resp.json()
            return [Candle(**r) for r in ret]

    async def get_currency(self, currency_id: str) -> Currency:
       async with self._session.get(self._make_url(f"currencies/{currency_id}")) as resp:
           ret = await resp.json()
           return Currency(**ret)

    # async def create(self, title: str, text: str) -> Post:
    #     async with self._session.post(
    #         self._make_url("api"),
    #         json={"owner": self._user, "title": title, "text": text},
    #     ) as resp:
    #         ret = await resp.json()
    #         return Post(**ret["data"])
    # async def delete(self, post_id: int) -> None:
    #     async with self._session.delete(self._make_url(f"api/{post_id}")) as resp:
    #         resp  # to make linter happy

    #async def update(
    #    self, post_id: int, title: Optional[str] = None, text: Optional[str] = None
    #) -> Post:
    #    json = {"editor": self._user}
    #    if title is not None:
    #        json["title"] = title
    #    if text is not None:
    #        json["text"] = text
    #    async with self._session.patch(
    #        self._make_url(f"api/{post_id}"), json=json
    #    ) as resp:
    #        ret = await resp.json()
    #        return Post(**ret["data"])

    #async def list(self) -> List[Post]:
    #    async with self._session.get(self._make_url(f"api")) as resp:
    #        ret = await resp.json()
    #        return [Post(text=None, **item) for item in ret["data"]]



async def main():
    url = URL("https://api.exchange._cb.com")
    user = "givenskm"
    async with _cbClient(url, user) as client:
        ticker = await client.get_ticker('BTC-USD')
        print("ticker: ", ticker)
        # stats = await client.get_stats('BTC-USD')
        # print("stats: ", stats)
        # ccy_info = await client.get_currency('BTC')
        # print("ccy: ", ccy_info)


if __name__ == "__main__":
    asyncio.run(main())