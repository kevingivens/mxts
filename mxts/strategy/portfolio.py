import pandas as pd
from typing import List, Union, TYPE_CHECKING
from mxts.core import Instrument, ExchangeType, Position

if TYPE_CHECKING:
    from mxts.engine import StrategyManager
    from mxts.engine.managers import Portfolio


class StrategyPortfolioMixin(object):
    _manager: "StrategyManager"

    def positions(
        self, instrument: Instrument = None, exchange: ExchangeType = None
    ) -> List[Position]:
        """select all positions

        Args:
            instrument (Instrument): filter positions by instrument
            exchange (ExchangeType): filter positions by exchange
        Returns:
            list (Position): list of positions
        """
        return self._manager.positions(
            strategy=self, instrument=instrument, exchange=exchange  # type: ignore # mixin
        )

    def portfolio(self) -> "Portfolio":
        """Get portfolio object"""
        return self._manager.portfolio()

    def price_history(self, instrument: Instrument = None) -> Union[dict, pd.DataFrame]:
        """Get price history for asset

        Args:
            instrument (Instrument): get price history for instrument
        Returns:
            DataFrame: price history
        """
        return self._manager.price_history(instrument=instrument)
