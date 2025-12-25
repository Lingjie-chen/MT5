import streamlit as st
import pandas as pd
import time
from datetime import datetime
import sys
import os
import json

# Ensure python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from python.database_manager import DatabaseManager
from python.visualization import TradingVisualizer

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
symbol = st.sidebar.text_input("Symbol", value="GOLD").upper()
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 60, 5)
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)

# Main Dashboard
st.title(f"🚀 AI Quant Trading Dashboard - {symbol}")

# Status Placeholders
header_col1, header_col2, header_col3 = st.columns(3)
with header_col1:
    st.markdown("### Market Status")
    status_placeholder = st.empty()
with header_col2:
    st.markdown("### AI Decision")
    ai_decision_placeholder = st.empty()
with header_col3:
    st.markdown("### Last Update")
    time_placeholder = st.empty()

# Layout
# Top Row: Chart (Left) and Stats (Right)
row1_col1, row1_col2 = st.columns([7, 3])

with row1_col1:
    st.subheader(f"{symbol} Market Analysis")
    chart_placeholder = st.empty()

with row1_col2:
    st.subheader("Signal & Portfolio Status")
    gauge_placeholder = st.empty()
    pie_placeholder = st.empty()

# Bottom Row: Equity Curve and Recent Trades
row2_col1, row2_col2 = st.columns([1, 1])

with row2_col1:
    st.subheader("Equity Curve")
    equity_placeholder = st.empty()

with row2_col2:
    st.subheader("Trading Blotter")
    trades_table_placeholder = st.empty()

st.markdown("---")
# AI Analysis Section
st.subheader("🤖 AI Market Insights (DeepSeek & Qwen)")
ai_analysis_placeholder = st.container()

st.subheader("Recent Signals")
signals_table_placeholder = st.empty()

def load_data():
    # Load Market Data
    market_df = db_manager.get_market_data(symbol, limit=200)
    
    # Load Signals
    signals_df = db_manager.get_latest_signals(limit=50)
    
    # Load Trades
    trades_df = db_manager.get_trades(limit=100)
    
    return market_df, signals_df, trades_df

def update_dashboard():
    market_df, signals_df, trades_df = load_data()
    
    # 1. Update Header Info
    current_price = 0.0
    if not market_df.empty:
        current_price = market_df.iloc[-1]['close']
        prev_price = market_df.iloc[-2]['close'] if len(market_df) > 1 else current_price
        delta = current_price - prev_price
        status_placeholder.metric("Current Price", f"{current_price:.2f}", f"{delta:.2f}")
    else:
        status_placeholder.warning("Waiting for market data...")

    last_signal = None
    if not signals_df.empty:
        # Filter for current symbol if needed
        symbol_signals = signals_df[signals_df['symbol'] == symbol]
        if not symbol_signals.empty:
            last_signal = symbol_signals.iloc[0]
            ai_decision_placeholder.info(f"{last_signal['signal'].upper()} (Strength: {last_signal['strength']:.1f}%)")
            
            # Update Gauge
            fig_gauge = visualizer.create_gauge_chart(last_signal['strength'], title=f"Signal Strength: {last_signal['strength']:.1f}")
            gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True)

            # Update AI Analysis Text
            with ai_analysis_placeholder:
                try:
                    details = json.loads(last_signal['details'])
                    
                    # Extract Key AI Insights
                    market_state = details.get('market_state', 'N/A')
                    prediction = details.get('prediction', 'N/A')
                    adv_summary = details.get('adv_summary', {})
                    if isinstance(adv_summary, str): # Handle if it's a string
                         st.info(adv_summary)
                    elif isinstance(adv_summary, dict):
                         summary_text = adv_summary.get('summary', 'No summary available')
                         regime = adv_summary.get('regime_analysis', 'N/A')
                         st.markdown(f"**Market State:** {market_state} | **Prediction:** {prediction}")
                         st.markdown(f"**Technical Summary:** {summary_text}")
                         st.markdown(f"**Regime Analysis:** {regime}")
                    
                    # Show Reasons/Signals
                    with st.expander("Detailed Strategy Signals", expanded=False):
                        st.json(details.get('signals', {}))
                        
                except Exception as e:
                    st.error(f"Failed to parse AI details: {e}")

    else:
        ai_decision_placeholder.text("No signals yet")

    time_placeholder.text(datetime.now().strftime("%H:%M:%S"))

    # 2. Update Charts
    if not market_df.empty:
        latest_details = last_signal['details'] if last_signal is not None else None
        fig_main = visualizer.create_advanced_chart(market_df, signals_df, trades_df, latest_details)
        chart_placeholder.plotly_chart(fig_main, use_container_width=True)
    
    # 3. Update Pie Chart (Win/Loss)
    if not trades_df.empty:
        fig_pie = visualizer.create_pnl_distribution(trades_df)
        pie_placeholder.plotly_chart(fig_pie, use_container_width=True)
        
        # Update Equity Curve
        fig_equity = visualizer.create_equity_curve(trades_df)
        equity_placeholder.plotly_chart(fig_equity, use_container_width=True)

        # Update Trades Table (Styled)
        trades_display = trades_df[['time', 'action', 'price', 'volume', 'profit']].head(10).copy()
        # Simple styling: color profit
        def color_profit(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'white'
            return f'color: {color}'
        
        # trades_table_placeholder.dataframe(trades_display.style.applymap(color_profit, subset=['profit']), use_container_width=True)
        trades_table_placeholder.dataframe(trades_display, use_container_width=True)

    # 4. Update Signals Table
    if not signals_df.empty:
        signals_table_placeholder.dataframe(signals_df[['timestamp', 'symbol', 'signal', 'strength', 'source']].head(5), use_container_width=True)


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
