import streamlit as st
import pandas as pd
import time
from datetime import datetime
import sys
import os
import json

# Ensure python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gold'))

from gold.database_manager import DatabaseManager
from gold.visualization import TradingVisualizer

# Page Config
st.set_page_config(
    page_title="AI Quant Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cyberpunk Styling
def apply_cyberpunk_style():
    st.markdown("""
        <style>
        /* Global App Background */
        .stApp {
            background-color: #050505;
            background-image: 
                radial-gradient(circle at 50% 50%, #111119 0%, #000000 100%);
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
        }
        
        /* Headers - Neon Glow */
        h1, h2, h3 {
            color: #00f3ff !important;
            text-shadow: 0 0 8px rgba(0, 243, 255, 0.6), 0 0 16px rgba(0, 243, 255, 0.4);
            font-family: 'Orbitron', 'Courier New', sans-serif;
            font-weight: 700;
            letter-spacing: 1px;
        }
        
        /* Metrics - Cyberpunk Style */
        div[data-testid="stMetric"] {
            background-color: rgba(10, 10, 15, 0.8);
            border: 1px solid #333;
            border-left: 3px solid #ff00ff;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(255, 0, 255, 0.1);
        }
        div[data-testid="stMetricLabel"] {
            color: #888 !important;
            font-size: 0.8rem;
        }
        div[data-testid="stMetricValue"] {
            color: #ff00ff !important;
            text-shadow: 0 0 5px rgba(255, 0, 255, 0.5);
            font-family: 'Courier New', monospace;
        }
        div[data-testid="stMetricDelta"] {
            color: #00ff9d !important;
        }
        
        /* Dataframes/Tables - Dark & Techy */
        .stDataFrame {
            border: 1px solid #333;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
        }
        
        /* Sidebar - Dark Panel */
        section[data-testid="stSidebar"] {
            background-color: #08080c;
            border-right: 1px solid #1f1f2e;
        }
        section[data-testid="stSidebar"] h1 {
            text-shadow: none;
            color: #fff !important;
        }
        
        /* Containers & Expanders */
        .streamlit-expanderHeader {
            background-color: #0f0f15 !important;
            color: #00f3ff !important;
            border: 1px solid #1f1f2e;
            border-radius: 4px;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #1f1f2e;
            background-color: rgba(10, 10, 16, 0.5);
        }
        
        /* Buttons - Neon Outlines */
        .stButton > button {
            background-color: transparent;
            color: #00f3ff;
            border: 1px solid #00f3ff;
            border-radius: 0;
            box-shadow: 0 0 5px rgba(0, 243, 255, 0.2);
            font-family: 'Courier New', monospace;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: rgba(0, 243, 255, 0.1);
            color: #fff;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.5);
            border-color: #fff;
        }
        
        /* Alerts/Info Boxes */
        div[data-testid="stAlert"] {
            background-color: rgba(0, 20, 40, 0.6);
            border: 1px solid #00f3ff;
            color: #e0e0e0;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            background: #050505;
        }
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00f3ff;
        }
        </style>
    """, unsafe_allow_html=True)

apply_cyberpunk_style()

# Initialize Managers
# Remove cache_resource to ensure latest class definition is loaded during dev
@st.cache_resource 
def get_managers():
    db = DatabaseManager("trading_data.db")
    viz = TradingVisualizer()
    return db, viz

db_manager, visualizer = get_managers()

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

def update_dashboard():
    for symbol, tab in zip(selected_symbols, tabs):
        with tab:
            render_symbol_dashboard(symbol)

def render_symbol_dashboard(symbol):
    st.header(f"{symbol} Overview")
    
    # Load Data specific to symbol
    market_df = db_manager.get_market_data(symbol, limit=200)
    signals_df = db_manager.get_latest_signals(limit=50) # Need to filter by symbol later
    trades_df = db_manager.get_trades(limit=100) # Need to filter by symbol later
    
    # Filter Dataframes
    if not signals_df.empty:
        signals_df = signals_df[signals_df['symbol'] == symbol]
    if not trades_df.empty:
        trades_df = trades_df[trades_df['symbol'] == symbol]

    # Status Placeholders
    header_col1, header_col2, header_col3 = st.columns(3)
    
    # 1. Update Header Info
    current_price = 0.0
    if not market_df.empty:
        current_price = market_df.iloc[-1]['close']
        prev_price = market_df.iloc[-2]['close'] if len(market_df) > 1 else current_price
        delta = current_price - prev_price
        header_col1.metric("Current Price", f"{current_price:.2f}", f"{delta:.2f}")
    else:
        header_col1.warning("Waiting for market data...")

    last_signal = None
    if not signals_df.empty:
        last_signal = signals_df.iloc[0]
        header_col2.info(f"{last_signal['signal'].upper()} (Strength: {last_signal['strength']:.1f}%)")
        header_col3.text(f"Last Update: {last_signal['timestamp']}")
    else:
        header_col2.text("No signals yet")
        header_col3.text(datetime.now().strftime("%H:%M:%S"))

    # Layout
    row1_col1, row1_col2 = st.columns([7, 3])

    with row1_col1:
        st.subheader(f"Market Analysis")
        if not market_df.empty:
            latest_details = last_signal['details'] if last_signal is not None else None
            # Use visualizer (assuming it handles plotting)
            fig_main = visualizer.create_advanced_chart(market_df, signals_df, trades_df, latest_details)
            st.plotly_chart(fig_main, use_container_width=True, key=f"chart_{symbol}")
        else:
            st.info("Chart waiting for data...")

    with row1_col2:
        st.subheader("Signal Strength")
        if last_signal is not None:
            fig_gauge = visualizer.create_gauge_chart(last_signal['strength'], title=f"Strength")
            st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{symbol}")
        
        st.subheader("Win/Loss Ratio")
        if not trades_df.empty:
            fig_pie = visualizer.create_pnl_distribution(trades_df)
            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{symbol}")

    # Bottom Row: Equity Curve and Recent Trades
    row2_col1, row2_col2 = st.columns([1, 1])

    with row2_col1:
        st.subheader("Equity Curve")
        if not trades_df.empty:
            fig_equity = visualizer.create_equity_curve(trades_df)
            st.plotly_chart(fig_equity, use_container_width=True, key=f"equity_{symbol}")
        else:
            st.info("No trades executed yet.")

    with row2_col2:
        st.subheader("Recent Trades")
        if not trades_df.empty:
            trades_display = trades_df[['time', 'action', 'price', 'volume', 'profit']].head(10).copy()
            st.dataframe(trades_display, use_container_width=True)
        else:
            st.info("No trade history.")

    st.markdown("---")
    # AI Analysis Section
    st.subheader("🤖 AI Market Insights")
    if last_signal is not None:
        try:
            details = json.loads(last_signal['details'])
            
            # Extract Key AI Insights
            market_state = details.get('market_state', 'N/A')
            prediction = details.get('prediction', 'N/A')
            reason = details.get('reason', 'N/A')
            
            # Override Alert
            if '[Override]' in reason:
                st.error(f"🔥 STRATEGY OVERRIDE ACTIVATED: {reason}")
            else:
                st.info(f"Strategy Logic: {reason}")
            
            adv_summary = details.get('adv_summary', {})
            if isinstance(adv_summary, str): 
                    st.markdown(f"**Technical Summary:** {adv_summary}")
            elif isinstance(adv_summary, dict):
                    summary_text = adv_summary.get('summary', 'No summary available')
                    regime = adv_summary.get('regime_analysis', 'N/A')
                    st.markdown(f"**Market State:** {market_state} | **Prediction:** {prediction}")
                    st.markdown(f"**Regime Analysis:** {regime}")
                    st.markdown(f"**Technical Summary:** {summary_text}")
            
            # Consensus Analysis
            signals_map = details.get('signals', {})
            if signals_map:
                buy_count = sum(1 for v in signals_map.values() if v == 'buy')
                sell_count = sum(1 for v in signals_map.values() if v == 'sell')
                total_valid = sum(1 for v in signals_map.values() if v not in ['neutral', 'hold'])
                
                st.markdown("### 📊 Algo Consensus")
                col_c1, col_c2, col_c3 = st.columns(3)
                col_c1.metric("Buy Votes", f"{buy_count}", delta=f"{buy_count/len(signals_map):.0%}" if signals_map else None)
                col_c2.metric("Sell Votes", f"{sell_count}", delta=f"-{sell_count/len(signals_map):.0%}" if signals_map else None, delta_color="inverse")
                col_c3.metric("Active Signals", f"{total_valid}/{len(signals_map)}")
            
            # Show Reasons/Signals
            with st.expander("Detailed Strategy Signals", expanded=False):
                st.json(signals_map)
                
        except Exception as e:
            st.error(f"Failed to parse AI details: {e}")


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
