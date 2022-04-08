import asyncio
# from typing import TYPE_CHECKING, Callable, Optional, Tuple

from mxts.config.enums import EventType
from ..data.event import Event

def callback(*events):
    def inner(func):
        if not hasattr(func, 'registered'):
            setattr(func, 'registered', True)
            setattr(func, 'events', events)
        return func
    return inner

class EventHandler():
    
    def __init__(self) -> None:
        cb_names = [m for m in dir(self) if m.startswith("on_")]
        self.callbacks = {m: getattr(getattr(self, m), 'events', []) for m in cb_names}
        
    #################################################
    # Event Handler Callback                        #
    #                                               #
    # NOTE: these should all be of the form on_noun #
    #################################################

    @callback(EventType.TRADE)
    async def on_trade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""
        #print("calling on_trade")
        await asyncio.sleep(2)
        return

    @callback(EventType.OPEN, EventType.CANCEL)
    async def on_order(self, event: Event) -> None:
        """EventType: Open, Cancel, Change, Fill"""
        pass

    @callback(EventType.OPEN)
    async def on_open(self, event: Event) -> None:
        """ EventType: Open"""
        pass

    @callback(EventType.CANCEL)
    async def on_cancel(self, event: Event) -> None:
        """Called whenever an Order `Cancel` event is received"""
        pass

    @callback(EventType.CHANGE)    
    async def on_change(self, event: Event) -> None:
        """Called whenever an Order `Change` event is received"""
        pass

    @callback(EventType.FILL)
    async def on_fill(self, event: Event) -> None:
        """Called whenever an Order `Fill` event is received"""
        pass

    @callback(EventType.DATA)
    async def on_data(self, event: Event) -> None:
        """Called whenever other data is received"""

    @callback(EventType.HALT)
    async def on_halt(self, event: Event) -> None:
        """Called whenever an exchange `Halt` event is received, i.e. an event to stop trading"""
        pass

    @callback(EventType.CONTINUE)
    async def on_continue(self, event: Event) -> None:
        """Called whenever an exchange `Continue` event is received, i.e. an event to continue trading"""
        pass

    @callback(EventType.ERROR)
    async def on_error(self, event: Event) -> None:
        """Called whenever an internal error occurs"""
        pass

    @callback(EventType.START)
    async def on_start(self, event: Event) -> None:
        """Called once at engine initialization time"""
        pass

    @callback(EventType.EXIT)
    async def on_exit(self, event: Event) -> None:
        """Called once at engine exit time"""
        pass

    ################################################
    # Order Entry Callbacks                        #
    #                                              #
    # NOTE: these should all be of the form on_verb#
    ################################################
    @callback(EventType.BOUGHT)
    async def on_bought(self, event: Event) -> None:
        """Called on my order bought"""
        pass

    @callback(EventType.SOLD)
    async def on_sold(self, event: Event) -> None:
        """Called on my order sold"""
        pass

    @callback(EventType.BOUGHT, EventType.SOLD) 
    async def on_traded(self, event: Event) -> None:
        """Called on my order bought or sold"""
        pass

    @callback(EventType.RECEIVED)
    async def on_received(self, event: Event) -> None:
        """Called on my order received by exchange"""
        pass

    @callback(EventType.REJECTED)    
    async def on_rejected(self, event: Event) -> None:
        """Called on my order rejected"""
        pass

    @callback(EventType.CANCELED)    
    async def on_canceled(self, event: Event) -> None:
        """Called on my order canceled"""
        pass
