import asyncio

from yarl import URL



async def main():
    url = URL("https://api.exchange.coinbase.com")
    async with CoinbaseClient(url) as client:
        ticker = await client.get_ticker('BTC-USD')
        print("ticker: ", ticker)
        stats = await client.get_stats('BTC-USD')
        print("stats: ", stats)
        ccy_info = await client.get_currency('BTC')
        print("ccy: ", ccy_info)


if __name__ == "__main__":
    asyncio.run(main())