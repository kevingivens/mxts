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



if __name__ == "__main__":
    from decimal import Decimal
    from cryptofeed.types import Balance
 

    s = '{"__portfolio__":true, "positions":[{"exchange":"COINBASE","currency":"USD","balance":"100000.0000000000000000","reserved":"0E-16"},{"exchange":"COINBASE","currency":"USD","balance":"100000.0000000000000000","reserved":"0E-16"}]}'

    data = {
        "id": "fe3587a8-693b-45c7-a22f-bba9cd15dd86",
        "currency": "USD",        
        "balance": "100000.0000000000000000",
        "hold": "0.0000000000000000",
        "available": "100000.0000000000000000"
    }

    b1 = Balance(
        'COINBASE',
        data['currency'],
        Decimal(data['balance']),
        Decimal(data['balance']) - Decimal(data['available'])
    )
    
    portfolio = Portfolio([b1, b1])

    print(portfolio.balance)
    
    #print(json.dumps(portfolio))

    p2 = load(s)

    print(p2.balance)

    # print(p2.positions)
  


    