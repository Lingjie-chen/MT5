import streamlit as st
import pandas as pd
import time
from datetime import datetime
import json
# Ensure python path
import os
import sys

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
    st.header(f"{symbol} Overview")
    
    # Initialize DB Manager for this specific symbol
    db_manager = get_db_manager(symbol)
    
    # Load Data specific to symbol
    market_df = db_manager.get_market_data(symbol, limit=200)
    signals_df = db_manager.get_latest_signals(limit=50) 
    trades_df = db_manager.get_trades(limit=100) 
    
    # Note: Since DBs are now isolated, filtering by symbol is technically redundant 
    # but kept for safety if schemas change.
    
    # Filter Dataframes
    if not signals_df.empty and 'symbol' in signals_df.columns:
        signals_df = signals_df[signals_df['symbol'] == symbol]
    if not trades_df.empty and 'symbol' in trades_df.columns:
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
    # AI Analysis Section - Clean Layout
    st.subheader("🤖 AI Market Insights")
    
    if last_signal is not None:
        try:
            details = json.loads(last_signal['details'])
            reason = details.get('reason', 'N/A')
            
            # 1. Main Strategy Logic Box
            if '[Override]' in reason:
                st.error(f"🔥 **Override Strategy Active**\n\n{reason}")
            else:
                st.info(f"💡 **Strategy Logic**\n\n{reason}")
            
            # 2. Detailed Breakdown Columns
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.markdown("#### 📈 Market State")
                market_state = details.get('market_state', 'N/A')
                prediction = details.get('prediction', 'N/A')
                st.success(f"**State:** {market_state}")
                st.warning(f"**Prediction:** {prediction}")

                # Regime Analysis if available
                adv_summary = details.get('adv_summary', {})
                if isinstance(adv_summary, dict):
                    regime = adv_summary.get('regime_analysis', 'N/A')
                    st.markdown(f"**Regime:** {regime}")

            with col_d2:
                st.markdown("#### 📊 Algo Consensus")
                signals_map = details.get('signals', {})
                if signals_map:
                    buy_count = sum(1 for v in signals_map.values() if v == 'buy')
                    sell_count = sum(1 for v in signals_map.values() if v == 'sell')
                    total = len(signals_map)
                    
                    st.progress(buy_count / total if total > 0 else 0, text=f"Buy Votes: {buy_count}")
                    st.progress(sell_count / total if total > 0 else 0, text=f"Sell Votes: {sell_count}")
            
            # 3. Technical Summary (Collapsible)
            with st.expander("📝 Technical Analysis Summary", expanded=False):
                if isinstance(adv_summary, str): 
                    st.markdown(adv_summary)
                elif isinstance(adv_summary, dict):
                    st.markdown(adv_summary.get('summary', 'No summary available'))
                
                st.markdown("#### Detailed Signal Inputs")
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
