import logging

from .client import OandaClient
from .client import __version__
from .definitions import *
from .endpoints.annotations import *

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = __version__
