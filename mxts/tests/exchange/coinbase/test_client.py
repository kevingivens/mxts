import pytest

async def test_get_products(client: CoinbaseClient) -> None:
    result = await client.get_products()


async def test_get_product(client: CoinbaseClient) -> None:
    result = await client.get_product("BTC-USD")
    assert