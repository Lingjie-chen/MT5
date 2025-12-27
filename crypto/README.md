# OKX Crypto Trading Strategy

This project is a quantitative trading strategy designed for OKX cryptocurrency exchange, based on an AI-driven architecture using DeepSeek and Qwen models.

## Project Structure

- `crypto/trading_bot.py`: Main entry point for the trading bot. Orchestrates data fetching, AI analysis, and trade execution.
- `crypto/okx_data_processor.py`: Handles interaction with OKX API via `ccxt`. Fetches OHLCV data and calculates technical indicators (EMA, RSI, ATR).
- `crypto/ai_client_factory.py`: Factory for creating AI clients.
- `crypto/deepseek_client.py`: Client for DeepSeek API (Market Structure Analysis).
- `crypto/qwen_client.py`: Client for Qwen API (Strategy Optimization and Decision Making).
- `crypto/database_manager.py`: Manages the SQLite database for trade logging.
- `crypto/.env`: Configuration file for API keys.
- `crypto/requirements.txt`: Python dependencies.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r crypto/requirements.txt
    ```

2.  **Configuration**:
    The `crypto/.env` file has been pre-configured with your provided OKX API keys.
    **Note**: You need to add your `SILICONFLOW_API_KEY` to the `.env` file for the AI models to work.

3.  **Run the Bot**:
    To run a single pass of the strategy:
    ```bash
    python crypto/trading_bot.py
    ```
    
    Or use the watchdog script to keep it running:
    ```bash
    ./crypto/run_bot_watchdog.sh
    ```

## Strategy Logic

1.  **Data Acquisition**: Fetches historical candle data from OKX.
2.  **Feature Engineering**: Calculates technical indicators (EMA, RSI, ATR, Volatility).
3.  **Market Analysis (DeepSeek)**: Analyzes market structure, support/resistance, and trends.
4.  **Decision Making (Qwen)**: Combines market analysis with technical signals to generate trading decisions (Buy/Sell/Hold) and manage risk (Stop Loss/Take Profit).
5.  **Execution**: Executes trades on OKX (currently in logging mode, uncomment execution lines in `trading_bot.py` to enable live trading).

## Notes

- The bot currently logs actions instead of executing real trades for safety. Review `trading_bot.py`'s `execute_trade` method to enable real orders.
- Ensure your API keys have the necessary permissions (Trade, Read).
