from turtle import position
from unicodedata import numeric
import numpy as np
from yapic import json
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from cryptofeed.types import Balance


def _hook(data):
    if "__portfolio__" in data:
        return Portfolio([json.loads(ps, parse_float=Decimal) for ps in data["positions"]])

def load(data):
    return json.loads(data, object_hook=_hook)


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
        return {"__portfolio__": True, "positions": [ps.to_dict(numeric_type=str) for ps in self.positions]}

    @property
    def balance(self):
        """return value of portfolio"""
        return np.sum([ps.balance for ps in self.positions])



