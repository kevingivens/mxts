from typing import Any, AsyncIterator, Awaitable, Callable, List, Optional, Type

from pydantic import BaseModel
from pandas import Timestamp

from .enums import *

class Ticker(BaseModel):
    trade_id: int
    price: float
    size: float
    time: Timestamp # str frmt '2022-03-16T15:44:59.735466Z'
    bid: float
    ask: float
    volume: float


class Fees(BaseModel):
    maker_fee_rate: float
    taker_fee_rate: float
    usd_volume: Optional[float]


class Stats(BaseModel):
    open: float
    high: float
    low: float
    last: float
    volume: float
    volume_30day: float


class Account(BaseModel):
    id: str
    currency: str
    balance: float
    hold: float
    available: float
    profile_id: str
    trading_enabled: bool


class Candle(BaseModel):
    times: Timestamp
    low: float
    high: float
    open: float
    close: float
    volume: float


class CurrencyDetail(BaseModel): 
    type: str
    symbol: Optional[str]
    network_confirmations: int
    sort_order: int
    crypto_address_link: str
    crypto_transaction_link: str
    push_payment_methods: List[str]
    group_types: Optional[List]
    display_name: Optional[str]
    processing_time_seconds: Optional[int]
    min_withdrawal_amount: float
    max_withdrawal_amount: float


class Currency(BaseModel):
    id: str
    name: str
    min_size: float
    status: str
    message: Optional[str]
    max_precision: float
    convertible_to: Optional[List]
    details: CurrencyDetail


class LedgerEntity(BaseModel):
    type: EntryType = None