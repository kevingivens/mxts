from enum import Enum

class Stp(str, Enum):
    dc = 'dc'
    co = 'co'
    cn = 'cn'
    cb = 'cb'


class Stop(str, Enum):
    loss = 'loss'
    entry = 'entry'


class TradeSide(str, Enum):
    buy = 'buy'
    sell = 'sell'


class TradeType(str, Enum):
    limit = 'limit'
    market = 'market'
    stop = 'stop'


class TimeInForce(str, Enum):
    GTC = 'GTC'
    GTT = 'GTT'
    IOC = 'IOC'
    FOK = 'FOK'


class CancelAfter(str, Enum):
    min = 'min'
    hour = 'hour'
    day = 'day'
    

class EntryType(str, Enum):
    transfer = 'transfer'
    match = 'match'
    fee = 'fee'
    rebate = 'rebate'
    conversion = 'conversion'
