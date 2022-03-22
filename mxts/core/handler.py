from abc import ABCMeta, abstractmethod
from inspect import isabstract
from typing import TYPE_CHECKING, Callable, Optional, Tuple
from ..data import Event
from ..config import EventType

if TYPE_CHECKING:
    # Circular import
    from mxts.engine import StrategyManager


class EventHandler(metaclass=ABCMeta):
    _manager: "StrategyManager"

    def _setManager(self, mgr: "StrategyManager") -> None:
        self._manager = mgr

    def _valid_callback(self, callback: str) -> Optional[Callable]:
        """
        TODO: turn this into wrapper ?
        """
        if (
            hasattr(self, callback)
            and not isabstract(callback)
            and not hasattr(getattr(self, callback), "_original")
        ):
            return getattr(self, callback)
        return None
    
    def callback(self, event_type: EventType) -> Tuple[Optional[Callable], ...]:
        return {
            # Market data
            EventType.TRADE: (self._valid_callback("onTrade"),),
            EventType.OPEN: (
                self._valid_callback("onOpen"),
                self._valid_callback("onOrder"),
            ),
            EventType.CANCEL: (
                self._valid_callback("onCancel"),
                self._valid_callback("onOrder"),
            ),
            EventType.CHANGE: (
                self._valid_callback("onChange"),
                self._valid_callback("onOrder"),
            ),
            EventType.FILL: (
                self._valid_callback("onFill"),
                self._valid_callback("onOrderEvent"),
            ),
            EventType.DATA: (self._valid_callback("onData"),),
            EventType.HALT: (self._valid_callback("onHalt"),),
            EventType.CONTINUE: (self._valid_callback("onContinue"),),
            EventType.ERROR: (self._valid_callback("onError"),),
            EventType.START: (self._valid_callback("onStart"),),
            EventType.EXIT: (self._valid_callback("onExit"),),
            # Order Entry
            EventType.BOUGHT: (
                self._valid_callback("onBought"),
                self._valid_callback("onTraded"),
            ),
            EventType.SOLD: (
                self._valid_callback("onSold"),
                self._valid_callback("onTraded"),
            ),
            EventType.RECEIVED: (self._valid_callback("onReceived"),),
            EventType.REJECTED: (self._valid_callback("onRejected"),),
            EventType.CANCELED: (self._valid_callback("onCanceled"),),
        }.get(event_type, tuple())

    ################################################
    # Event Handler Methods                        #
    #                                              #
    # NOTE: these should all be of the form onNoun #
    ################################################

    @abstractmethod
    async def on_trade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""

    async def on_order(self, event: Event) -> None:
        """Called whenever an Order `Open`, `Cancel`, `Change`, or `Fill` event is received"""
        pass

    async def on_open(self, event: Event) -> None:
        """Called whenever an Order `Open` event is received"""
        pass

    async def on_cancel(self, event: Event) -> None:
        """Called whenever an Order `Cancel` event is received"""
        pass

    async def on_change(self, event: Event) -> None:
        """Called whenever an Order `Change` event is received"""
        pass

    async def on_fill(self, event: Event) -> None:
        """Called whenever an Order `Fill` event is received"""
        pass

    async def on_data(self, event: Event) -> None:
        """Called whenever other data is received"""

    async def on_halt(self, event: Event) -> None:
        """Called whenever an exchange `Halt` event is received, i.e. an event to stop trading"""
        pass

    async def on_continue(self, event: Event) -> None:
        """Called whenever an exchange `Continue` event is received, i.e. an event to continue trading"""
        pass

    async def on_error(self, event: Event) -> None:
        """Called whenever an internal error occurs"""
        pass

    async def on_start(self, event: Event) -> None:
        """Called once at engine initialization time"""
        pass

    async def on_exit(self, event: Event) -> None:
        """Called once at engine exit time"""
        pass

    ################################################
    # Order Entry Callbacks                        #
    #                                              #
    # NOTE: these should all be of the form onVerb #
    ################################################
    async def on_bought(self, event: Event) -> None:
        """Called on my order bought"""
        pass

    async def on_sold(self, event: Event) -> None:
        """Called on my order sold"""
        pass

    async def on_traded(self, event: Event) -> None:
        """Called on my order bought or sold"""
        pass

    async def on_received(self, event: Event) -> None:
        """Called on my order received by exchange"""
        pass

    async def on_rejected(self, event: Event) -> None:
        """Called on my order rejected"""
        pass

    async def on_canceled(self, event: Event) -> None:
        """Called on my order canceled"""
        pass
