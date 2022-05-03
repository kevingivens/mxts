from cryptofeed.defines import COINBASE
from pydantic import BaseSettings, PositiveInt

from .enums import TradingType


class Settings(BaseSettings):
    # run in verbose mode (print all events)
    verbose = True

    # Trading type
    trading_type: TradingType = TradingType.SANDBOX
    
    # Engine heartbeat interval in seconds 
    heartbeat: PositiveInt = 10

    # Load account information from exchanges
    load_accounts = True

    # universe of trading symbols
    symbols = ['BTC-USD', 'ETH-USD']
    
    # exchanges to communicate with
    exchanges = [COINBASE]

    # local path to portfolio io
    portfolio_fp: str

    alpha_models: List[AlphaModel] = []
    

   


