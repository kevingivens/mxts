import logging

from oanda.client import OandaClient
from oanda.client import __version__
from oanda.definitions import *
from oanda.endpoints.annotations import *

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = __version__
