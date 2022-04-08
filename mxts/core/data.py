from typing import Any, Callable, Optional, List

from pandas import Timestamp
from pydantic import BaseModel

from ..config.enums import (
    DataType, 
    EventType, 
    ExchangeType,
    InstrumentType, 
    Side, 
    OptionType,
    OrderType,
    OrderFlag
)

# TODO: check slots behavour BaseModel

class Event(BaseModel):
    type: EventType
    data: Any


class Error(BaseModel):
    type: DataType = DataType.ERROR
    data: Any
    timestamp: Timestamp = Timestamp.now()
    exception: BaseException
    callback: Callable


class Instrument(BaseModel):
    """
    Args:
        name (str): the asset's common name, relative to whatever
                    the exchange's standard is
        type (InstrumentType): the instrument type, dictates the required
                               extra kwargs
        exchange (ExchangeType): the exchange the instrument can be traded
                                 through
        trading_day (TradingDay): per-exchange trading hours
            Applies to: All
        broker_exchange (str): Underlying exchange to use (e.g. not aat.exchange,
                              but real exchange in cases where aat is wrapping a
                              broker like IB, TDA, etc)
            Applies to: All
        broker_id (str): Broker's id  if available
            Applies to: All
        currency (Instrument): Underlying currency
            Applies to: All
        underlying (Instrument): the underlying asset
            Applies to: OPTION, FUTURE, FUTURESOPTION
        leg1 (Instrument):
            Applies to: PAIR, SPREAD
        leg2 (Instrument):
            Applies to: PAIR, SPREAD
        leg1_side (Side):
            Applies to: SPREAD
        leg2_side (Side):
            Applies to: SPREAD
    """
    exchange: ExchangeType
    type: InstrumentType
    broker_id: Optional[str]
    currency: Optional["Instrument"]
    underlying: Optional["Instrument"]
    leg1: Optional["Instrument"]
    leg2: Optional["Instrument"]
    leg1_side: Optional[Side]
    leg2s_side: Optional[Side]
    expiration: Optional[Timestamp]
    contract_month: Optional[int]
    price_increment: Optional[float]
    unit_value: Optional[float]
    option_type: Optional[OptionType]


class Order(BaseModel):
    id: int
    timestamp: Timestamp = Timestamp.now()
    type: InstrumentType
    instrument: Instrument
    exchange: ExchangeType
    volume: float
    price: float
    notional: float = 0.0
    filled: float
    side: Side
    order_type: OrderType = OrderType.MARKET
    flag: OrderFlag = OrderFlag.NONE
    stop_target: Optional["Order"]
    force_done: bool


class Trade(BaseModel):
    id: int
    type = DataType.TRADE
    price: float
    volume: float
    my_order: str
    maker_orders: Optional[List[Order]] = None
    taker_order: Order
    slippage = 0.0
    transaction_cost = 0.0
    # assert volume == taker_order.filled