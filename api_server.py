from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import json
import pandas as pd

# Ensure python path to import DatabaseManager
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from python.database_manager import DatabaseManager

app = FastAPI()

# CORS for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()

@app.get("/api/market-data/{symbol}")
def get_market_data(symbol: str, limit: int = 100):
    # Map BTC/USDT to standard format if needed, but DB uses what's saved.
    # Assuming symbol in DB matches user input (e.g., GOLD)
    clean_symbol = symbol.replace("/", "") # GOLD vs BTCUSDT
    
    df = db.get_market_data(clean_symbol, limit)
    if df.empty:
        # Fallback to GOLD if specific symbol not found (for demo)
        df = db.get_market_data("GOLD", limit)
        
    if df.empty:
        return []
        
    # Format for React App: { time, open, high, low, close, volume }
    # React expects string time, usually HH:MM:SS for intraday
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
    return df[['time', 'open', 'high', 'low', 'close', 'volume']].to_dict(orient='records')

import numpy as np

def calculate_sharpe_ratio(trades_df):
    if trades_df.empty:
        return 0.0
    # Approximate Sharpe from trade returns
    # Assuming risk-free rate is 0 for simplicity
    returns = trades_df['profit']
    if len(returns) < 2:
        return 0.0
    
    std_dev = returns.std()
    if std_dev == 0:
        return 0.0
        
    avg_return = returns.mean()
    sharpe = (avg_return / std_dev) * np.sqrt(len(trades_df)) # Annualized roughly? No, just trade-based Sharpe
    # For a proper Sharpe we need periodic returns. 
    # Let's stick to a simple Mean/StdDev of trade profits for now as a proxy
    return round(float(avg_return / std_dev), 2)

def calculate_max_drawdown(trades_df, initial_balance=10000.0):
    if trades_df.empty:
        return 0.0
        
    # Reconstruct equity curve
    cumulative_profit = trades_df['profit'].cumsum()
    equity_curve = initial_balance + cumulative_profit
    
    peak = equity_curve.cummax()
    drawdown = (equity_curve - peak) / peak * 100
    return round(float(abs(drawdown.min())), 2)

@app.get("/api/signals")
def get_signals(limit: int = 50):
    df = db.get_latest_signals(limit)
    if df.empty:
        return []
    
    # Filter for GOLD
    df = df[df['symbol'].str.contains('GOLD', case=False, na=False) | df['symbol'].str.contains('XAU', case=False, na=False)]
    
    result = []
    for _, row in df.iterrows():
        try:
            details = json.loads(row['details']) if row['details'] else {}
        except:
            details = {}
            
        # Construct a readable reasoning string
        reasoning = "AI Analysis Completed"
        if 'adv_summary' in details:
            adv = details['adv_summary']
            if isinstance(adv, dict):
                reasoning = adv.get('summary', reasoning)
            elif isinstance(adv, str):
                reasoning = adv
        elif 'crt_reason' in details:
            reasoning = details['crt_reason']
            
        result.append({
            "timestamp": row['timestamp'],
            "symbol": row['symbol'],
            "type": row['signal'].upper(),
            "strength": float(row['strength']),
            "reasoning": reasoning,
            "source": row['source']
        })
    return result

@app.get("/api/trades")
def get_trades(limit: int = 50):
    df = db.get_trades(limit)
    if df.empty:
        return []
        
    # Filter for GOLD
    df = df[df['symbol'].str.contains('GOLD', case=False, na=False) | df['symbol'].str.contains('XAU', case=False, na=False)]
    
    result = []
    for _, row in df.iterrows():
        status = "PENDING"
        if row['result'] == 'CLOSED':
            status = "FILLED" # In this UI, FILLED/CLOSED are similar concepts of past trades
        elif row['result'] == 'OPEN':
            status = "PENDING" # Active trade
            
        result.append({
            "id": str(row['ticket']),
            "time": row['time'],
            "symbol": row['symbol'],
            "side": row['action'],
            "price": float(row['price']),
            "amount": float(row['volume']),
            "pnl": float(row['profit']) if pd.notna(row['profit']) else 0.0,
            "status": status
        })
    return result

@app.get("/api/analysis/latest")
def get_latest_analysis():
    df = db.get_latest_signals(limit=1)
    if df.empty:
        return None
    
    row = df.iloc[0]
    try:
        details = json.loads(row['details']) if row['details'] else {}
    except:
        details = {}
        
    adv_summary = details.get('adv_summary', {})
    summary_text = "Analysis available"
    regime = "Neutral"
    
    if isinstance(adv_summary, dict):
        summary_text = adv_summary.get('summary', summary_text)
        regime = adv_summary.get('regime_analysis', regime)
    elif isinstance(adv_summary, str):
        summary_text = adv_summary
        
    return {
        "summary": summary_text,
        "regime": regime,
        "confidence": float(row['strength']),
        "riskAssessment": details.get('market_state', 'Moderate'),
        "nextTarget": 0.0
    }

@app.get("/api/metrics")
def get_metrics():
    # Try to get real-time account metrics from DB first
    metrics = db.get_latest_account_metrics()
    
    # Get trades for stats calculation
    trades = db.get_trades(limit=1000)
    # Filter for GOLD as requested
    gold_trades = trades[trades['symbol'].str.contains('GOLD', case=False, na=False) | trades['symbol'].str.contains('XAU', case=False, na=False)] if not trades.empty else pd.DataFrame()

    closed_trades = gold_trades[gold_trades['result'] == 'CLOSED'] if not gold_trades.empty else pd.DataFrame()
    
    # Calculate common stats
    win_rate = 0.0
    sharpe = 0.0
    drawdown = 0.0
    
    if not closed_trades.empty:
        wins = len(closed_trades[closed_trades['profit'] > 0])
        total = len(closed_trades)
        win_rate = (wins / total * 100) if total > 0 else 0
        sharpe = calculate_sharpe_ratio(closed_trades)

    # Initialize variables
    current_equity = 10000.0
    current_balance = 10000.0
    daily_pnl = 0.0
    daily_pnl_percent = 0.0
    equity_change_percent = 0.0
    
    if metrics:
        # Use real MT5 account info
        current_balance = metrics['balance']
        current_equity = metrics['equity']
        
        # Calculate Equity Change (24h)
        hist_metrics = db.get_historical_account_metrics(hours_ago=24)
        if hist_metrics and hist_metrics['equity'] > 0:
            equity_change_percent = ((current_equity - hist_metrics['equity']) / hist_metrics['equity']) * 100
        
        # Calculate Daily P&L (Equity change since start of day)
        start_day_metrics = db.get_start_of_day_metrics()
        if start_day_metrics:
            daily_pnl = current_equity - start_day_metrics['equity']
            if start_day_metrics['equity'] > 0:
                daily_pnl_percent = (daily_pnl / start_day_metrics['equity']) * 100
        else:
            # Fallback: Realized Today + Floating
            today = pd.Timestamp.now().date()
            if not closed_trades.empty:
                 # Ensure close_time is datetime
                closed_trades['close_time'] = pd.to_datetime(closed_trades['close_time'])
                today_trades = closed_trades[closed_trades['close_time'].dt.date == today]
                realized_today = today_trades['profit'].sum() if not today_trades.empty else 0.0
            else:
                realized_today = 0.0
            
            floating = metrics.get('total_profit', 0.0)
            daily_pnl = realized_today + floating
            if current_balance > 0:
                daily_pnl_percent = (daily_pnl / current_balance) * 100

        drawdown = calculate_max_drawdown(closed_trades, current_balance)

    else:
        # Fallback to calculated metrics from trades only
        total_pnl = closed_trades['profit'].sum() if not closed_trades.empty else 0
        current_balance = 10000.0 + total_pnl
        current_equity = current_balance # No floating PnL known
        
        today = pd.Timestamp.now().date()
        if not closed_trades.empty:
            closed_trades['close_time'] = pd.to_datetime(closed_trades['close_time'])
            today_trades = closed_trades[closed_trades['close_time'].dt.date == today]
            daily_pnl = today_trades['profit'].sum() if not today_trades.empty else 0.0
        
        if current_balance > 0:
             daily_pnl_percent = (daily_pnl / current_balance) * 100
             
        drawdown = calculate_max_drawdown(closed_trades, 10000.0)

    return {
        "balance": current_balance,
        "equity": current_equity,
        "equityChange": f"{'+' if equity_change_percent >= 0 else ''}{equity_change_percent:.2f}%",
        "dailyPnL": daily_pnl,
        "dailyPnLPercent": f"{'+' if daily_pnl_percent >= 0 else ''}{daily_pnl_percent:.2f}%",
        "winRate": round(win_rate, 2),
        "sharpeRatio": sharpe,
        "maxDrawdown": drawdown
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting API Server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
