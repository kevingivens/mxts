from typing import TYPE_CHECKING

from mxts.core import Position

if TYPE_CHECKING:
    from mxts.engine import StrategyManager


class StrategyRiskMixin(object):
    _manager: "StrategyManager"

    def risk(self, position: Position = None) -> dict:
        """Get risk metrics

        Args:
            position (Position): only get metrics on this position
        Returns:
            dict: metrics
        """
        return self._manager.risk(position=position)
