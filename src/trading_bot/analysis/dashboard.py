import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import os
import sys
import yfinance as yf
import plotly.graph_objects as go

# Add project root to sys.path to ensure correct imports
# dashboard.py is at src/trading_bot/analysis/dashboard.py
# We want to add the project root (MT5/) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

if project_root not in sys.path:
    sys.path.append(project_root)

# Import using full package paths
try:
    from src.trading_bot.data.database_manager import DatabaseManager
    from src.trading_bot.analysis.visualization import TradingVisualizer
except ImportError:
    # Fallback for relative run
    sys.path.append(os.path.join(project_root, 'src'))
    from trading_bot.data.database_manager import DatabaseManager
    from trading_bot.analysis.visualization import TradingVisualizer

# Page Config
st.set_page_config(
    page_title="AI Quant Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean Professional Styling
def apply_clean_style():
    st.markdown("""
        <style>
        /* Global App Background */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #ffffff !important;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-weight: 600;
        }
        
        /* Metrics */
        div[data-testid="stMetric"] {
            background-color: #1e2127;
            border: 1px solid #2e3136;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        div[data-testid="stMetricLabel"] {
            color: #b0b0b0 !important;
            font-size: 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-family: 'Segoe UI', sans-serif;
        }
        
        /* Dataframes */
        .stDataFrame {
            border: 1px solid #2e3136;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161920;
            border-right: 1px solid #2e3136;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #262730;
            color: #ffffff;
            border: 1px solid #4f5359;
            border-radius: 4px;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            border-color: #ffffff;
            background-color: #363940;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            color: #b0b0b0;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: #ffffff;
            border-bottom: 2px solid #4f8bf9;
        }
        
        </style>
    """, unsafe_allow_html=True)

apply_clean_style()

# Initialize Managers
# Remove cache_resource to ensure latest class definition is loaded during dev
# No longer creating a single global db_manager
@st.cache_resource 
def get_visualizer():
    viz = TradingVisualizer()
    return viz

visualizer = get_visualizer()

# Sidebar Settings
st.sidebar.title("Configuration")
# Changed to multiselect for multi-symbol support
available_symbols = ["GOLD", "ETHUSD", "EURUSD"]
selected_symbols = st.sidebar.multiselect("Select Symbols", available_symbols, default=["GOLD"])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 60, 5)
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)

# Main Dashboard
st.title("🚀 AI Multi-Symbol Trading Dashboard")

if not selected_symbols:
    st.warning("Please select at least one symbol from the sidebar.")
    st.stop()

# Create tabs for each selected symbol
tabs = st.tabs(selected_symbols)

# Mapping for YFinance
SYMBOL_MAP = {
    "GOLD": "GC=F", # Gold Futures
    "XAUUSD": "GC=F",
    "EURUSD": "EURUSD=X",
    "ETHUSD": "ETH-USD",
    "BTCUSD": "BTC-USD",
}

@st.cache_data(ttl=60) # Cache for 1 min
def fetch_online_price(symbol, period="1d", interval="15m"):
    """Fetch real-time data from Yahoo Finance"""
    try:
        ticker = SYMBOL_MAP.get(symbol.upper(), symbol)
        # Handle XAUUSD specifically if not found
        if "XAU" in symbol.upper(): ticker = "GC=F"
        
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if df is None or df.empty:
            return None
        
        # Handle MultiIndex columns (yfinance > 0.2.0)
        # If columns are MultiIndex, the second level is usually the Ticker
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.droplevel(1)
            except:
                pass # Try to proceed if droplevel fails
            
        # Standardize columns
        df.reset_index(inplace=True)
        df.columns = [c.lower() for c in df.columns]
        
        # Ensure timestamp column is named 'timestamp' or 'date'
        if 'date' in df.columns:
            df.rename(columns={'date': 'timestamp'}, inplace=True)
        elif 'datetime' in df.columns:
            df.rename(columns={'datetime': 'timestamp'}, inplace=True)
            
        return df
    except Exception as e:
        st.error(f"Failed to fetch online data: {e}")
        return None

def get_db_manager(symbol):
    """Dynamically get the DatabaseManager for a specific symbol"""
    db_filename = f"trading_data_{symbol}.db"
    # Assuming the DBs are in the 'gold' directory relative to this script
    db_path = os.path.join(os.path.dirname(__file__), 'gold', db_filename)
    return DatabaseManager(db_path=db_path)

def update_dashboard():
    for symbol, tab in zip(selected_symbols, tabs):
        with tab:
            render_symbol_dashboard(symbol)

def render_symbol_dashboard(symbol):
    # Initialize DB Manager
    db_manager = get_db_manager(symbol)
    
    # --- Data Loading ---
    # 1. Local DB Data
    local_market_df = db_manager.get_market_data(symbol, limit=200)
    signals_df = db_manager.get_latest_signals(limit=50) 
    trades_df = db_manager.get_trades(limit=1000) # Fetch more for equity curve
    
    # 2. Online Data (Real-time Trend)
    online_df = fetch_online_price(symbol, period="5d", interval="15m")
    
    # Filter Dataframes
    if not signals_df.empty and 'symbol' in signals_df.columns:
        signals_df = signals_df[signals_df['symbol'] == symbol]
    if not trades_df.empty and 'symbol' in trades_df.columns:
        trades_df = trades_df[trades_df['symbol'] == symbol]

    # --- Header Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Live Price (Priority: Online > Local)
    current_price = 0.0
    delta = 0.0
    
    if online_df is not None and not online_df.empty:
        # Check if 'close' is a tuple (MultiIndex) or Series
        try:
            # yfinance > 0.2 returns MultiIndex columns sometimes
            close_data = online_df['close'].squeeze()
            
            current_price = float(close_data.iloc[-1])
            prev_price = float(close_data.iloc[-2])
            delta = current_price - prev_price
            source = "🟢 Live (Net)"
        except Exception as e:
             st.error(f"Error parsing online data: {e}")
             source = "🔴 Error"
    elif not local_market_df.empty:
        current_price = local_market_df.iloc[-1]['close']
        prev_price = local_market_df.iloc[-2]['close'] if len(local_market_df) > 1 else current_price
        delta = current_price - prev_price
        source = "🟠 Local DB"
    else:
        source = "⚪ No Data"

    col1.metric(f"{symbol} Price", f"{current_price:,.2f}", f"{delta:,.2f}")
    col2.caption(f"Source: {source}")
    
    # Signal Status
    last_signal = None
    if not signals_df.empty:
        last_signal = signals_df.iloc[0]
        sig_color = "green" if last_signal['signal'] == 'buy' else "red" if last_signal['signal'] == 'sell' else "gray"
        col3.markdown(f"**Latest Signal:** :{sig_color}[{last_signal['signal'].upper()}]")
        col4.markdown(f"**Strength:** {last_signal['strength']:.1f}%")

    # --- Tabs Layout ---
    tab_overview, tab_account, tab_ai, tab_trades = st.tabs(["📈 Market Overview", "💰 Account & Assets", "🤖 AI Strategy", "📝 Trade History"])
    
    with tab_overview:
        st.subheader("Price Trend (Real-time)")
        
        # Chart Selection
        chart_source = st.radio("Chart Source", ["Internet (Live)", "Bot Data (Signals)"], horizontal=True)
        
        if chart_source == "Internet (Live)":
            if online_df is not None and not online_df.empty:
                # Prepare data safely using squeeze() to handle single-col DataFrame or Series
                o = online_df['open'].squeeze()
                h = online_df['high'].squeeze()
                l = online_df['low'].squeeze()
                c = online_df['close'].squeeze()
                
                # Simple Candlestick for Internet Data
                fig = go.Figure(data=[go.Candlestick(
                    x=online_df['timestamp'],
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    increasing_line_color='#00ff9d', decreasing_line_color='#ff0055'
                )])
                fig.update_layout(height=500, template="plotly_dark", title=f"{symbol} Live Trend (Yahoo Finance)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Online data unavailable. Please check your internet connection.")
                
        else: # Bot Data
            if not local_market_df.empty:
                latest_details = last_signal['details'] if last_signal is not None else None
                fig_main = visualizer.create_advanced_chart(local_market_df, signals_df, trades_df, latest_details)
                st.plotly_chart(fig_main, use_container_width=True, key=f"chart_local_{symbol}")
            else:
                st.info("No local market data collected yet.")

    with tab_account:
        col_acc1, col_acc2 = st.columns([2, 1])
        
        with col_acc1:
            st.subheader("Equity Curve & Asset Growth")
            if not trades_df.empty:
                fig_equity = visualizer.create_equity_curve(trades_df)
                st.plotly_chart(fig_equity, use_container_width=True, key=f"equity_{symbol}")
            else:
                st.info("No trades to display equity curve.")
                
        with col_acc2:
            st.subheader("Performance Metrics")
            if not trades_df.empty:
                closed_trades = trades_df[trades_df['result'] == 'CLOSED']
                total_trades = len(closed_trades)
                if total_trades > 0:
                    net_profit = closed_trades['profit'].sum()
                    wins = len(closed_trades[closed_trades['profit'] > 0])
                    win_rate = (wins / total_trades) * 100
                    
                    st.metric("Net Profit", f"${net_profit:,.2f}")
                    st.metric("Total Trades", total_trades)
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                    
                    # Pie Chart
                    fig_pie = visualizer.create_pnl_distribution(trades_df)
                    st.plotly_chart(fig_pie, use_container_width=True, height=200)
                else:
                    st.info("No closed trades yet.")
            else:
                st.info("No trade data.")

    with tab_ai:
        st.subheader("🤖 AI Market Insights")
        if last_signal is not None:
            try:
                details = json.loads(last_signal['details'])
                
                # Logic Box
                reason = details.get('reason', 'N/A')
                st.info(f"💡 **Strategy Logic:** {reason}")
                
                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Market State", details.get('market_state', 'N/A'))
                c2.metric("Prediction", details.get('prediction', 'N/A'))
                
                # Signal Gauge
                with c3:
                    fig_gauge = visualizer.create_gauge_chart(last_signal['strength'], title="Confidence")
                    st.plotly_chart(fig_gauge, use_container_width=True, height=150)
                
                # Technical Details
                with st.expander("Detailed Analysis"):
                    st.json(details)
                    
            except Exception as e:
                st.error(f"Error parsing AI details: {e}")
        else:
            st.info("No AI analysis available yet.")

    with tab_trades:
        st.subheader("Trade History")
        if not trades_df.empty:
            st.dataframe(
                trades_df[['ticket', 'time', 'action', 'price', 'volume', 'profit', 'result', 'close_time']].sort_values('time', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No trade history.")


# Main Loop
if auto_refresh:
    update_dashboard()
    time.sleep(refresh_rate)
    st.rerun()
else:
    if st.button("Refresh Now"):
        update_dashboard()
    else:
        update_dashboard()
