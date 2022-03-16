import pytest

from .fixtures.server import create_dummy_server


@pytest.fixture(name='dummy_server')
async def _dummy_server(aiohttp_server):
    return await create_dummy_server(aiohttp_server)