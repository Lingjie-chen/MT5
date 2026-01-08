I have updated the Qwen client strategy prompt for the crypto module to match your requirements. The gold module was already aligned with these rules.

**Changes Implemented:**

1.  **File Updated**: `crypto/qwen_client.py`
    *   **Added Critical Rule**: inserted the rule about the **15-minute (M15)** trading cycle combined with **H1** and **H4** trend analysis.
    *   **Updated Trend Cycle Control**:
        *   **Refuse Frequent Trading**: Explicitly stated not to trade every candle.
        *   **Trend Following**: emphasized **HOLD** until the trend ends.
        *   **Trend End Determination**: Defined exit criteria based on structure break or profit targets.
        *   **New Analysis**: Restricted new analysis to after the current trend ends.

2.  **File Verified**: `gold/qwen_client.py`
    *   Confirmed that it already contains the exact "Trend Cycle Control" and Critical Rules as requested.

The crypto strategy is now synchronized with the gold strategy regarding trading frequency and trend following rules.