I will resolve the `TypeError` crash and the persistent symbol warning with the following steps:

1.  **Fix `TypeError` in `execute_trade`**:
    -   The crash `argument of type 'int' is not iterable` happens because `execute_trade` currently assigns integer constants (e.g., `mt5.ORDER_TYPE_BUY`) to `trade_type`, but the downstream function `_send_order` expects a string (e.g., `"buy"`).
    -   **Action**: Update `src/trading_bot/main.py` to assign string values (`"buy"`, `"sell"`, `"limit_buy"`, `"limit_sell"`) to `trade_type` instead of MT5 constants.

2.  **Fix "Symbol info not found" Warning**:
    -   The previous optimization checked `symbol_info` before selecting. However, if a symbol is not yet in the Market Watch, `symbol_info` might return `None`.
    -   **Action**: Modify the logic in `process_tick` so that if `symbol_info` returns `None`, we force a `mt5.symbol_select(self.symbol, True)` call immediately, and then check `symbol_info` again. This ensures the symbol is loaded if it was missing.

**Verification**:
-   I will verify the fix by running a compilation check and ensuring the bot starts without immediate crashes.
-   The "Symbol info not found" warning should disappear or be replaced by a successful recovery log.
