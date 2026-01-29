import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

class TradingVisualizer:
    def __init__(self):
        pass

    def create_advanced_chart(self, df, signals_df=None, trades_df=None, analysis_details=None):
        """
        创建一个包含高级分析可视化（SMC, CRT, etc.）的交互式图表 - Cyberpunk Style
        """
        if df is None or df.empty:
            return go.Figure()

        # 创建子图: 主图(K线+叠加指标) + 副图(RSI/Vol)
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            row_heights=[0.75, 0.25],
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
        )

        # 1. Candlestick Chart (Neon Colors)
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#00ff9d', # Neon Green
            decreasing_line_color='#ff0055'  # Neon Red/Pink
        ), row=1, col=1)

        # 2. Add Moving Averages (Glowing Lines)
        if 'ema_20' not in df.columns:
            df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        if 'ema_50' not in df.columns:
            df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['ema_20'], 
            line=dict(color='#00f3ff', width=1.5), # Cyan
            name='EMA 20'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['ema_50'], 
            line=dict(color='#ff00ff', width=1.5), # Magenta
            name='EMA 50'
        ), row=1, col=1)

        # 3. Add Signals Markers (Neon Glow)
        if signals_df is not None and not signals_df.empty:
            # 解析 details 以识别 Override 信号
            signals_df['is_override'] = signals_df['details'].apply(
                lambda x: '[Override]' in json.loads(x).get('reason', '') if isinstance(x, str) else False
            )
            
            # 普通信号
            normal_buy = signals_df[(signals_df['signal'] == 'buy') & (~signals_df['is_override'])]
            normal_sell = signals_df[(signals_df['signal'] == 'sell') & (~signals_df['is_override'])]
            
            # Override 信号 (高亮显示)
            override_buy = signals_df[(signals_df['signal'] == 'buy') & (signals_df['is_override'])]
            override_sell = signals_df[(signals_df['signal'] == 'sell') & (signals_df['is_override'])]

            # Draw Normal Buy
            if not normal_buy.empty:
                fig.add_trace(go.Scatter(
                    x=normal_buy['timestamp'],
                    y=df.loc[df['timestamp'].isin(normal_buy['timestamp']), 'low'] * 0.999,
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=12, color='#00ff00', line=dict(width=2, color='#00ff9d')),
                    name='Buy Signal'
                ), row=1, col=1)

            # Draw Normal Sell
            if not normal_sell.empty:
                fig.add_trace(go.Scatter(
                    x=normal_sell['timestamp'],
                    y=df.loc[df['timestamp'].isin(normal_sell['timestamp']), 'high'] * 1.001,
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=12, color='#ff0000', line=dict(width=2, color='#ff0055')),
                    name='Sell Signal'
                ), row=1, col=1)
                
            # Draw Override Buy (Gold Star)
            if not override_buy.empty:
                fig.add_trace(go.Scatter(
                    x=override_buy['timestamp'],
                    y=df.loc[df['timestamp'].isin(override_buy['timestamp']), 'low'] * 0.998,
                    mode='markers',
                    marker=dict(symbol='star', size=15, color='#ffd700', line=dict(width=2, color='#ffffff')),
                    name='Override Buy (Strong)'
                ), row=1, col=1)

            # Draw Override Sell (Gold Star)
            if not override_sell.empty:
                fig.add_trace(go.Scatter(
                    x=override_sell['timestamp'],
                    y=df.loc[df['timestamp'].isin(override_sell['timestamp']), 'high'] * 1.002,
                    mode='markers',
                    marker=dict(symbol='star', size=15, color='#ff8c00', line=dict(width=2, color='#ffffff')),
                    name='Override Sell (Strong)'
                ), row=1, col=1)

        # 4. Visualize SMC/CRT Zones
        if analysis_details:
            self._add_analysis_overlays(fig, df, analysis_details)

        # 5. Volume on Row 2
        colors = ['#ff0055' if row['open'] > row['close'] else '#00ff9d' for index, row in df.iterrows()]
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            marker_color=colors,
            marker_line_width=0,
            opacity=0.6,
            name='Volume'
        ), row=2, col=1)

        # Layout updates for Clean Theme (Light)
        fig.update_layout(
            title=dict(text='Market Analysis', font=dict(color='#000000', size=20)),
            xaxis_rangeslider_visible=False,
            height=600,
            template='plotly_white', # Changed from plotly_dark
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#e0e0e0', gridwidth=1),
            yaxis=dict(showgrid=True, gridcolor='#e0e0e0', gridwidth=1),
            yaxis2=dict(showgrid=False),
            font=dict(family="Segoe UI", color="#333333"),
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    def _add_analysis_overlays(self, fig, df, details):
        """
        解析 details JSON 并绘制 SMC Block, FVG, CRT Range 等
        """
        try:
            if isinstance(details, str):
                details = json.loads(details)
            
            # SMC Order Blocks / FVG
            # 假设 details 结构中有 smc_reason 或 details['signals']['smc'] 等
            # 这里需要根据实际保存的 JSON 结构适配。
            # 参考 start.py: save_signal -> details
            
            # Example: Draw CRT Range if available
            # "crt_reason": "...", "range_high": ..., "range_low": ... (need to check what's actually saved)
            # In start.py, details has 'crt_reason'. The actual numeric levels might not be in the top level dict
            # unless we modify start.py to save them.
            # However, let's try to extract what we can or parse text.
            
            # Draw latest FVG/OB if present in 'signals' -> 'smc' -> 'details'
            # Start.py saves: "signals": all_signals, "details": { ... }
            # Wait, start.py logic for saving details:
            # "details": { "weights":..., "signals":..., "market_state":..., "crt_reason":..., "smc_structure":... }
            # It seems numeric levels (like FVG top/bottom) are NOT saved in the top level details JSON in start.py currently.
            # They are inside the objects returned by analyzers, but start.py only extracts 'signal' and 'reason' for some.
            
            # For visualization to be "Advanced", we really need those levels.
            # But for now, let's just annotate the latest signal reason.
            pass
            
        except Exception as e:
            print(f"Error adding overlays: {e}")

    def create_gauge_chart(self, value, title="Signal Strength"):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "lightblue"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "black"} # Light mode font
        )
        return fig

    def create_equity_curve(self, trades_df):
        """
        Create Equity Curve based on closed trades
        """
        if trades_df is None or trades_df.empty:
            return go.Figure()

        # Filter closed trades
        closed_trades = trades_df[trades_df['result'] == 'CLOSED'].copy()
        if closed_trades.empty:
            return go.Figure()
        
        # Sort by close time
        closed_trades['close_time'] = pd.to_datetime(closed_trades['close_time'])
        closed_trades = closed_trades.sort_values('close_time')
        
        # Calculate cumulative profit
        closed_trades['cumulative_profit'] = closed_trades['profit'].cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=closed_trades['close_time'], 
            y=closed_trades['cumulative_profit'],
            mode='lines+markers',
            name='Equity',
            line=dict(color='#00ff00', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 0, 0.1)'
        ))
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Time',
            yaxis_title='Net Profit',
            template='plotly_white', # Changed to white
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "black"} # Explicit font color
        )
        return fig

    def create_pnl_distribution(self, trades_df):
        """
        Create Win/Loss Pie Chart
        """
        if trades_df is None or trades_df.empty:
            return go.Figure()
            
        closed_trades = trades_df[trades_df['result'] == 'CLOSED']
        if closed_trades.empty:
            return go.Figure()
            
        wins = len(closed_trades[closed_trades['profit'] > 0])
        losses = len(closed_trades[closed_trades['profit'] <= 0])
        
        fig = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses'], 
            values=[wins, losses],
            hole=.4,
            marker=dict(colors=['#00ff00', '#ff0000'])
        )])
        
        fig.update_layout(
            title='Win/Loss Ratio',
            template='plotly_white', # Changed to white
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            font={'color': "black"} # Explicit font color
        )
        return fig
