from decimal import Decimal
from typing import List

from cryptofeed.types import Balance
import numpy as np
from yapic import json


def _from_dict(data):
    # TODO: merge into Balance class def
    b = Balance(
        'COINBASE',
        data['currency'],
        Decimal(data['balance']),
        Decimal(data['reserved'])
    )
    return b


def loads(data):
    positions = json.loads(data)
    portfolio = Portfolio([_from_dict(p) for p in positions])
    return portfolio
    

class Portfolio(object):
    """
    Stateful container of active postions
    
    Ideally, life cycle methods like loading and closing portfolio
    should be handled by Session context manager
    
    Args:
       

    """
    def __init__(self, positions):
       self.positions: List[Balance] = positions

    def __json__(self):
        return [ps.to_dict(numeric_type=str) for ps in self.positions]

    @property
    def balance(self):
        """return value of portfolio"""
        return np.sum([ps.balance for ps in self.positions])
