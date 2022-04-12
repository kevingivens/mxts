from typing import Any

import pytest
from aiohttp import web


async def get_product_ticker(request: web.Request) -> web.Response:
    return web.json_response({
        'ask': '40627.94',
        'bid': '40627.78',
        'volume': '19135.84426268',
        'trade_id': 297714496,
        'price': '40627.64',
        'size': '0.00830616',
        'time': '2022-03-16T15:44:59.735466Z'
    })


async def get_product_stats(request: web.Request) -> web.Response:
    return web.json_response({
        'open': '39020.82',
        'high': '41717.67',
        'low': '38850',
        'last': '40626.62',
        'volume': '19132.61811405',
        'volume_30day': '504815.87275369'
    })


async def get_product_info(request: web.Request) -> web.Response:
    return web.json_response({
        "id": "BTC-USD",
        "base_currency": "BTC",
        "quote_currency": "USD",
        "base_min_size": "0.000016",
        "base_max_size": "1500",
        "quote_increment": "0.01",
        "base_increment": "0.00000001",
        "display_name": "BTC/USD",
        "min_market_funds": "1",
        "max_market_funds": "20000000",
        "margin_enabled": False,
        "fx_stablecoin": False,
        "max_slippage_percentage": "0.02000000",
        "post_only": False,
        "limit_only": False,
        "cancel_only": False,
        "trading_disabled": False,
        "status": "online",
        "status_message": "",
        "auction_mode": False
    })

@pytest.fixture
@pytest.mark.asyncio
async def server(aiohttp_server: Any) -> web.Server:
    app = web.Application()
    app.add_routes(
        [
            web.get('/products/BTC-USD', get_product_info),
            web.get('/products/BTC-USD/stats', get_product_stats),
            web.get('/products/BTC-USD/ticker', get_product_ticker),
        ]
    )
    server = await aiohttp_server(app)
    return server


