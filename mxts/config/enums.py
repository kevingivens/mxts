from typing import List
from enum import Enum


class BaseEnum(Enum):
    def __str__(self) -> str:
        return f"{self.value}"

    @classmethod
    def members(cls) -> List[str]:
        return list(cls.__members__.keys())


class TradingType(BaseEnum):
    LIVE = "LIVE"
    SIMULATION = "SIMULATION"
    SANDBOX = "SANDBOX"
    BACKTEST = "BACKTEST"


class Side(BaseEnum):
    BUY = "BUY"
    SELL = "SELL"


class OptionType(BaseEnum):
    CALL = "CALL"
    PUT = "PUT"


class EventType(BaseEnum):
    # Heartbeat event
    HEARTBEAT = "HEARTBEAT"

    # Trade event
    TRADE = "TRADE"

    # Order events
    OPEN = "OPEN"
    CANCEL = "CANCEL"
    CHANGE = "CHANGE"
    FILL = "FILL"
    BOUGHT = "BOUGHT"
    SOLD = "SOLD"
    RECEIVED = "RECEIVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"

    # Other data event
    DATA = "DATA"

    # System events
    HALT = "HALT"
    CONTINUE = "CONTINUE"

    # Engine events
    ERROR = "ERROR"
    START = "START"
    EXIT = "EXIT"


class DataType(BaseEnum):
    DATA = "DATA"
    ERROR = "ERROR"
    ORDER = "ORDER"
    TRADE = "TRADE"


class InstrumentType(BaseEnum):
    EQUITY = "EQUITY"
    CURRENCY = "CURRENCY"
    INDEX = "INDEX"


class OrderType(BaseEnum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"


class OrderFlag(BaseEnum):
    NONE = "NONE"
    FILL_OR_KILL = "FILL_OR_KILL"
    ALL_OR_NONE = "ALL_OR_NONE"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"


class ExitRoutine(BaseEnum):
    NONE = "NONE"
    CLOSE_ALL = "CLOSE_ALL"
