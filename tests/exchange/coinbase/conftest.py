import pytest

from mxts.exchange.coinbase.client import CoinbaseClient

from .fixtures.server import server

server = server

@pytest.fixture
async def client() -> CoinbaseClient:
    async with CoinbaseClient() as client:
        yield client