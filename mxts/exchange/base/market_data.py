from abc import ABCMeta
from typing import AsyncIterator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mxts import Instrument, Event


class MarketData():
    """internal only class to represent the streaming-source
    side of a data source"""

    async def instruments(self) -> List[Instrument]:
        """get list of available instruments"""
        return []

    async def subscribe(self, instrument: Instrument) -> None:
        """subscribe to market data for a given instrument"""

    async def tick(self) -> AsyncIterator[Event]:
        """return data from exchange"""

    #async def book(self, instrument: Instrument) -> Optional[OrderBook]:
    #    """return order book"""