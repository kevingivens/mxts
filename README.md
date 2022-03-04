`mxts` is a python based multiexchange trading systems.  It is designed to be asynchronous, event-driven, and scalable. 

`mxts` system architecture is based on [aat](https://github.com/AsyncAlgoTrading/aat) with the CPU-bound event handling carried out by [Ray](https://github.com/ray-project/ray).

The exchange clients are based on [async_v20](https://github.com/jamespeterschinner/async_v20).

## Overview
Currently `mxts` supports access to [OANDA](https://www.oanda.com/us-en/) with [Coinbase](https://www.coinbase.com/) in development.