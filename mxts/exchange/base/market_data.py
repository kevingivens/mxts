from abc import ABCMeta
from typing import AsyncIterator, List, Optional, TYPE_CHECKING

from mxts.data import Instrument, Event

#if TYPE_CHECKING:
#    from mxts.data.instrument import Instrument
#    from mxts.data.event import Event


class MarketData:
    """mixin class to represent the streaming-source
    side of a data source
    
    TODO: add implementation logic if possible
    """

    async def instruments(self) -> List[Instrument]:
        """get list of available instruments"""
        return []

    async def subscribe(self, instrument: Instrument) -> None:
        """subscribe to market data for a given instrument"""

    async def tick(self) -> AsyncIterator[Event]:
        """return data from exchange"""

    #async def book(self, instrument: Instrument) -> Optional[OrderBook]:
    #    """return order book"""