I have updated the `crypto/trading_bot.py` and `gold/start.py` files to ensure the trading cycle is set to 15 minutes (M15).

**Changes Implemented:**

1.  **Crypto (`crypto/trading_bot.py`)**:
    *   Updated the `CryptoTradingBot` initialization default parameters to `timeframe='15m'` and `interval=900` (15 minutes).
    *   Updated the main execution block to instantiate the bot with `timeframe='15m'` and `interval=900`.

2.  **Gold (`gold/start.py`)**:
    *   Updated the main execution block to explicitly pass `timeframe=mt5.TIMEFRAME_M15` when creating the `AI_MT5_Bot` instance, ensuring the 15-minute cycle is enforced every time it runs.

The analysis and trading cycles for both strategies are now configured to operate on a 15-minute timeframe.