from abc import abstractmethod
from typing import Optional, TYPE_CHECKING
from mxts.core import Event
from mxts.core.handler import EventHandler


if TYPE_CHECKING:
    from .strategy import StrategyManager


class ManagerBase(EventHandler):
    @abstractmethod
    def _set_manager(self, mgr: "StrategyManager") -> None:
        """set the root manager"""

    async def on_bought(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        """Called on my order bought"""
        pass

    async def on_sold(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        """Called on my order sold"""
        pass

    async def on_traded(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        """Called on my order bought or sold"""
        pass

    async def on_received(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        """Called on my order received"""
        pass

    async def on_rejected(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        """Called on my order rejected"""
        pass

    async def on_canceled(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        """Called on my order canceled"""
        pass
