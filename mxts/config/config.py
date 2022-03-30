from typing import Optional

from pydantic import BaseSettings, BaseModel, Field, PositiveInt

from .enums import DateTimeFormat, TradingType, DateTimeFormat


class Settings(BaseSettings):
    verbose: bool = True
    trading_type: TradingType = TradingType.SANDBOX
    heartbeat: int = 10
    load_accounts: bool = True

    cb_key: str = Field(..., env='COINBASE_KEY')
    cb_secret: str = Field(..., env='COINBASE_SECRET')
    cb_passphrase: str = Field(..., env='COINBASE_PASSPHRASE')
    
    #class Config:
    #   """Loads the dotenv file."""
    #   env_file: str = ".env"

    #class Config:
    #    env_prefix = 'my_prefix_'  # defaults to no prefix, i.e. ""
    #    fields = {
    #        'auth_key': {
    #            'env': 'my_auth_key',
    #        },
    #    }

   
class GlobalConfig(BaseModel):
    """Global configurations"""

    # These variables will be loaded from the .env file. However, if
    # there is a shell environment variable having the same name,
    # that will take precedence.

    # run in verbose mode (print all events)
    verbose = True

    # Trading type
    trading_type: TradingType = TradingType.BACKTEST
    
    # Engine heartbeat interval in seconds 
    heartbeat: PositiveInt = 10

    # Load account information from exchanges
    load_accounts = True

    exchanges = []

    # define global variables with the Field class
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")

    # environment specific variables do not need the Field class
    # HOST: Optional[str] = None

    class Config:
        """Loads the dotenv file."""
        env_file: str = ".env"


class OandaConfig(GlobalConfig):
    """ OANDA session config object """
    #  token: User generated token from the online account configuration page
    # token: str = None
    
    # if token is None:
    #    token = os.environ['OANDA_TOKEN']
    
    # The account id the client will connect to. If None will default to
    # the first account number returned by :meth:`~oanda.OandaClient.list_accounts`
    
    account_id: Optional[str] = None
    
    # format_order_requests: 
    #   True = Format all OrderRequests in the context of the orders instrument. 
    #   False = Do not format OrderRequests,
    #   raise :class:`~oanda.exceptions.InvalidOrderRequest` for values outside of allowed range.
    format_order_requests = False
    
    # max_transaction_history: Maximum past transactions to store
    max_transaction_history: PositiveInt = 100
    
    # rest_host: The hostname of the REST server
    rest_host = 'api-fxpractice.oanda.com'
    
    # rest_port: The port of the REST server
    rest_port = 443
    
    # rest_scheme: The scheme of the connection to rest server.
    rest_scheme = 'https'

    # rest_timeout: The timeout to use when making a polling request with the REST server
    rest_timeout: PositiveInt = 10
        
    #  stream_host: The hostname of the REST server
    stream_host = 'stream-fxpractice.oanda.com'
    
    # stream_port: The port of the REST server
    stream_port: PositiveInt = None
    
    #  stream_scheme: The scheme of the connection to the stream server.
    stream_scheme = 'https'

    #  stream_timeout: Period to wait for an new json object during streaming
    stream_timeout: PositiveInt = 60
    
    # health_host: The hostname of the health API server
    health_host = 'api-status.oanda.com'
    
    # health_port: The port of the health server
    health_port = 80
    
    #  health_scheme: The scheme of the connection for the health server.
    health_scheme = 'http'
    
    #  datetime_format: The format to request when dealing with times
    datetime_format = DateTimeFormat.UNIX
    
    # max_requests_per_second: Maximum HTTP requests sent per second
    max_requests_per_second: PositiveInt = 99
    
    # max_simultaneous_connections: Maximum concurrent HTTP requests
    max_simultaneous_connections: PositiveInt = 10


#class CoinbaseConfig(GlobalConfig):
#    """ Coinbase session config object """
#
#    # rest_host: The hostname of the REST server
#    rest_host = 'api.pro.coinbase.com'
#    
#    # rest_port: The port of the REST server
#    rest_port = 443
#    
#    # rest_scheme: The scheme of the connection to rest server.
#    rest_scheme = 'https'
#
#    #  stream_host: The hostname of the WS server
#    stream_host = 'ws-feed.pro.coinbase.com'
#    
#    # stream_port: The port of the WS server
#    stream_port: PositiveInt = None
#    
#    #  stream_scheme: The scheme of the connection to the stream server.
#    stream_scheme = 'wss:'
#
#    # stream_timeout: Period to wait for an new json object during streaming
#    # stream_timeout: PositiveInt = 60
# 
#    # rest_sandbox = "https://api-public.sandbox.pro.coinbase.com"
#    
#    # ws_sandbox = "wss://ws-feed-public.sandbox.pro.coinbase.com"
#    
#    # subscription : Dict[str, Union[str, List[str]]] = {
#    #     "type": "subscribe",
#    #     "product_ids": [],
#    #     "channels": ["user", "heartbeat"],
#    # }
#    
#    # exchange: ExchangeType
#    
#    key: str
#    secret: str
#    passphrase: str

