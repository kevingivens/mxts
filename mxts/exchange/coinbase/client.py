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
   

class CoinbaseClient:
    def __init__(self, base_url: URL, **kwargs) -> None:
        self._base_url = base_url
        self._cb_secret = kwargs.get("cb_secret")
        self._cb_key = kwargs.get("cb_key")
        self._cb_passphrase = kwargs.get("cb_passphrase")
        self._session = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._session.close()

    async def __aenter__(self) -> "CoinbaseClient":
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
            method (str): HTTP verb
            url (str): url sub path
            body (str, optional): HTTP body params as string. Defaults to "".
   
        Returns:
            dict: headers
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

    async def get_accounts(self) -> List[Account]:
        url = self._make_url(f"accounts") 
        async with self._session.get(url, headers=self._hash_msg("GET", url.path)) as resp:
            ret = await resp.json()
            return [Account(**r) for r in ret]

    async def get_account(self, account_id: str) -> Account:
        url = self._make_url(f"accounts")
        async with self._session.get(url, headers=self._hash_msg("GET", url.path)) as resp:
            ret = await resp.json()
            return Account(**ret)

    async def convert_currency(self, **kwargs) -> Ticker:
        async with self._session.post(self._make_url("conversions"), json=kwargs) as resp:
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

    async def get_fills(self, **kwargs) -> List[Fill]:
        """ 
        kwargs:
            order_id str
                limit to fills on a specific order. Either order_id or product_id is required.
            product_id str 
                limit to fills on a specific product. Either order_id or product_id is required.
            profile_id str 
                get results for a specific profile
            limit int 
                Limit on number of results to return
            before int 
                Used for pagination. Sets start cursor to before date.
            after int 
                Used for pagination. Sets end cursor to after date.
        
        """
        async with self._session.get(self._make_url(f"fills", params=kwargs)) as resp:
            ret = await resp.json()
            return [Fill(**r) for r in ret]
    
    async def get_orders(self, **kwargs) -> List[Order]:
        """ 
        kwargs:
        profile_id str Filter results by a specific profile_id
        product_id str Filter results by a specific product_id
        sortedBy str Sort criteria for results.
        sorting str Ascending or descending order, by sortedBy
        desc start_date date-time Filter results by minimum posted date
        end_date date-time Filter results by maximum posted date
        before str Used for pagination. Sets start cursor to before date.
        after str Used for pagination. Sets end cursor to after date.
        limit int required Limit on number of results to return.
        100 status array of strings required
        Array with order statuses to filter by.
        
        """
        async with self._session.get(self._make_url(f"orders", params=kwargs)) as resp:
            ret = await resp.json()
            return [Order(**r) for r in ret]

    async def create_order(self, **kwargs) -> None:
        """ 
        kwargs:
        profile_id str Filter results by a specific profile_id
        product_id str Filter results by a specific product_id
        sortedBy str Sort criteria for results.
        sorting str Ascending or descending order, by sortedBy
        desc start_date date-time Filter results by minimum posted date
        end_date date-time Filter results by maximum posted date
        before str Used for pagination. Sets start cursor to before date.
        after str Used for pagination. Sets end cursor to after date.
        limit int required Limit on number of results to return.
        100 status array of strings required
        Array with order statuses to filter by.
        
        e.g. 
        json = {
            "profile_id": "default profile_id",
            "type": "limit",
            "side": "buy",
            "stp": "dc",
            "stop": "loss",
            "time_in_force": "GTC",
            "cancel_after": "min",
            "post_only": "false"
        }

        """
        async with self._session.post(self._make_url(f"orders", json=kwargs)) as resp:
            ret = await resp.json()
            return 

   
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

