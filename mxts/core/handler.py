import asyncio
# from typing import TYPE_CHECKING, Callable, Optional, Tuple

from mxts.config.enums import EventType
from ..data.event import Event

def callback(*events):
    def inner(func):
        if not hasattr(func, 'registered'):
            print("registering callback")
            setattr(func, 'registered', True)
            setattr(func, 'events', events)
            print("events: ", getattr(func, 'events'))
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
    async def on_trade(self, event: Event=None) -> None:
        """Called whenever a `Trade` event is received"""
        #print("calling on_trade")
        await asyncio.sleep(2)
        return

    @callback(EventType.OPEN, EventType.CANCEL)
    async def on_order(self, event: Event) -> None:
        """EventType: Open, Cancel, Change, Fill"""
        pass

    async def on_open(self, event: Event) -> None:
        """ EventType: Open"""
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
    # NOTE: these should all be of the form on_verb#
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
