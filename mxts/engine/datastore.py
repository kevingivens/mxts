import logging
from itertools import product
from contextlib import contextmanager

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class MarketDataStore:
    """

    Pub/Sub exchange object for publishing market stats
    
    args:
    queue: event queue
    pairs: ccy pairs
    length: (int) length of time series

    """
    def __init__(self, queue, pairs, length=10):
        self.queue = queue
        self.data = {pair: pd.DataFrame(columns=[f"{pair}_bid", f"{pair}_ask" ]) for pair in pairs}
        self.length = length
        self._subscribers = set()

    # pub/sub functionality 
    def attach(self, task):
        self._subscribers.add(task)
    
    def detach(self, task):
        self._subscribers.remove(task)
    
    @contextmanager
    def subscribe(self, *tasks):
        for task in tasks:
            self.attach(task)
        try:
            yield
        finally:
            for task in tasks:
                self.detach(task)
    
    def send(self, msg):
        """ send latests stats to subscribers """
        logger.info("Sending msg to subscribers")
        for s in self._subscribers:
            s.receive_msg(msg)
    
    def update_data(self, event):
        """ update data store with latest market data

        Args
        ----
        event (TickEvent)
        
        """
        data = self.data[event.instrument]

        data = data.append(
            pd.DataFrame(
                index=[event.time],
                data={
                    event.instrument + '_bid': [event.bid],
                    event.instrument + '_ask': [event.ask],
                }
            )
        )   
        
        if len(data) > self.length:
            data = data.drop(index=data.index[0])
        
        self.data[event.instrument] = data 
        
        self.send({event.instrument: self.compute_stats(data)})
    
    @staticmethod
    def compute_stats(data):
        desc = data.describe()
        latest = pd.DataFrame(data.iloc[0,:].to_dict(), index=["latest"])
        stats = pd.concat([desc, latest])
        return stats

