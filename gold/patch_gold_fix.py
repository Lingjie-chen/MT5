import re
import os

file_path = r'c:\Users\Administrator\Desktop\MT5\gold\start.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the pattern for the function
# We use a broad pattern that captures the function definition down to the return statement
pattern = re.compile(r'def calculate_optimized_sl_tp\(self, trade_type, price, atr, market_context=None\):.*?return final_sl, final_tp', re.DOTALL)

replacement = """def calculate_optimized_sl_tp(self, trade_type, price, atr, market_context=None, ai_exit_conds=None):
        \"\"\"
        计算基于综合因素的优化止损止盈点
        结合: 14天 ATR, MFE/MAE 统计, 市场分析(Supply/Demand/FVG), 大模型建议
        \"\"\"
        # 1. 基础波动率 (14天 ATR)
        if atr <= 0:
            atr = price * 0.005 # Fallback
            
        # 2. 历史绩效 (MFE/MAE)
        mfe_tp_dist = atr * 2.0 
        mae_sl_dist = atr * 1.5 
        
        try:
             stats = self.db_manager.get_trade_performance_stats(limit=100)
             trades = []
             if isinstance(stats, list): trades = stats
             elif isinstance(stats, dict) and 'recent_trades' in stats: trades = stats['recent_trades']
             
             if trades and len(trades) > 10:
                 mfes = [t.get('mfe', 0) for t in trades if t.get('mfe', 0) > 0]
                 maes = [abs(t.get('mae', 0)) for t in trades if abs(t.get('mae', 0)) > 0]
                 
                 if mfes and maes:
                     opt_tp_pct = np.percentile(mfes, 60) / 100.0 
                     opt_sl_pct = np.percentile(maes, 95) / 100.0 
                     
                     min_sl_dist = atr * 2.5
                     calc_sl_dist = price * opt_sl_pct
                     
                     mfe_tp_dist = price * opt_tp_pct
                     mae_sl_dist = max(calc_sl_dist, min_sl_dist) 
        except Exception as e:
             logger.warning(f"MFE/MAE 计算失败: {e}")

        # 3. 市场结构调整 (Supply/Demand/FVG)
        struct_tp_price = 0.0
        struct_sl_price = 0.0
        min_sl_buffer = atr * 2.0
        
        if market_context:
            is_buy = 'buy' in trade_type
            
            # 解析 SMC 关键位
            resistance_candidates = []
            support_candidates = []
            
            if is_buy:
                # Buy TP: Resistance
                if 'supply_zones' in market_context:
                    for z in market_context['supply_zones']:
                        val = z[1] if isinstance(z, (list, tuple)) else z.get('bottom')
                        if val and val > price: resistance_candidates.append(val)
                if 'bearish_fvgs' in market_context:
                    for f in market_context['bearish_fvgs']:
                        val = f.get('bottom')
                        if val and val > price: resistance_candidates.append(val)
                if resistance_candidates: struct_tp_price = min(resistance_candidates)
                
                # Buy SL: Support
                if 'demand_zones' in market_context:
                     for z in market_context['demand_zones']:
                        val = z[0] if isinstance(z, (list, tuple)) else z.get('top')
                        if val and val < price: support_candidates.append(val)
                if support_candidates: struct_sl_price = max(support_candidates)
                
            else: # Sell
                # Sell TP: Support
                if 'demand_zones' in market_context:
                    for z in market_context['demand_zones']:
                        val = z[0] if isinstance(z, (list, tuple)) else z.get('top')
                        if val and val < price: support_candidates.append(val)
                if 'bullish_fvgs' in market_context:
                    for f in market_context['bullish_fvgs']:
                        val = f.get('top')
                        if val and val < price: support_candidates.append(val)
                if support_candidates: struct_tp_price = max(support_candidates)
                
                # Sell SL: Resistance
                if 'supply_zones' in market_context:
                    for z in market_context['supply_zones']:
                        val = z[1] if isinstance(z, (list, tuple)) else z.get('bottom')
                        if val and val > price: resistance_candidates.append(val)
                if resistance_candidates: struct_sl_price = min(resistance_candidates)

        # 4. 大模型建议 (AI Integration)
        ai_sl = 0.0
        ai_tp = 0.0
        if ai_exit_conds:
            ai_sl = ai_exit_conds.get('sl_price', 0.0)
            ai_tp = ai_exit_conds.get('tp_price', 0.0)
            
            # Validate AI Suggestion Direction
            if 'buy' in trade_type:
                if ai_sl >= price: ai_sl = 0.0 # Invalid SL
                if ai_tp <= price: ai_tp = 0.0 # Invalid TP
            else:
                if ai_sl <= price: ai_sl = 0.0
                if ai_tp >= price: ai_tp = 0.0

        # 5. 综合计算与融合
        final_sl = 0.0
        final_tp = 0.0
        
        if 'buy' in trade_type:
            # --- SL Calculation ---
            base_sl = price - mae_sl_dist
            
            # Priority: AI -> Structure -> Statistical
            if ai_sl > 0:
                final_sl = ai_sl
            elif struct_sl_price > 0:
                final_sl = struct_sl_price if (price - struct_sl_price) >= min_sl_buffer else (price - min_sl_buffer)
            else:
                final_sl = base_sl
            
            if (price - final_sl) < min_sl_buffer:
                final_sl = price - min_sl_buffer
                
            # --- TP Calculation ---
            base_tp = price + mfe_tp_dist
            
            if ai_tp > 0:
                final_tp = ai_tp
            elif struct_tp_price > 0:
                final_tp = min(struct_tp_price - (atr * 0.1), base_tp)
            else:
                final_tp = base_tp
                
        else: # Sell
            # --- SL Calculation ---
            base_sl = price + mae_sl_dist
            
            if ai_sl > 0:
                final_sl = ai_sl
            elif struct_sl_price > 0:
                final_sl = struct_sl_price if (struct_sl_price - price) >= min_sl_buffer else (price + min_sl_buffer)
            else:
                final_sl = base_sl
                
            if (final_sl - price) < min_sl_buffer:
                final_sl = price + min_sl_buffer
                
            # --- TP Calculation ---
            base_tp = price - mfe_tp_dist
            
            if ai_tp > 0:
                final_tp = ai_tp
            elif struct_tp_price > 0:
                final_tp = max(struct_tp_price + (atr * 0.1), base_tp)
            else:
                final_tp = base_tp

        return final_sl, final_tp"""

new_content = pattern.sub(replacement, content, count=1)

if new_content == content:
    print("Pattern not found!")
else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File patched successfully.")
