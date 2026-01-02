import re
import os

file_path = r'c:\Users\Administrator\Desktop\MT5\gold\start.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the block to replace (using regex to be flexible with whitespace)
# We look for the block starting with "if has_new_params:" inside manage_positions
# and ending before "elif new_sl_multiplier > 0"

pattern = re.compile(r'if has_new_params:.*?elif new_sl_multiplier > 0', re.DOTALL)

replacement = """if has_new_params:
                # 使用 calculate_optimized_sl_tp 进行统一计算和验证
                ai_exits = strategy_params.get('exit_conditions', {})
                trade_dir = 'buy' if type_pos == mt5.POSITION_TYPE_BUY else 'sell'
                
                opt_sl, opt_tp = self.calculate_optimized_sl_tp(trade_dir, current_price, atr, market_context=None, ai_exit_conds=ai_exits)
                
                opt_sl = self._normalize_price(opt_sl)
                opt_tp = self._normalize_price(opt_tp)
                
                if opt_sl > 0:
                    diff_sl = abs(opt_sl - sl)
                    is_better_sl = False
                    if type_pos == mt5.POSITION_TYPE_BUY and opt_sl > sl: is_better_sl = True
                    if type_pos == mt5.POSITION_TYPE_SELL and opt_sl < sl: is_better_sl = True
                    
                    valid_sl = True
                    if type_pos == mt5.POSITION_TYPE_BUY and (current_price - opt_sl < stop_level_dist): valid_sl = False
                    if type_pos == mt5.POSITION_TYPE_SELL and (opt_sl - current_price < stop_level_dist): valid_sl = False
                    
                    if valid_sl and (diff_sl > point * 20 or (is_better_sl and diff_sl > point * 5)):
                        request['sl'] = opt_sl
                        changed = True
                        logger.info(f"AI/Stats 更新 SL: {sl:.2f} -> {opt_sl:.2f}")

                if opt_tp > 0:
                    diff_tp = abs(opt_tp - tp)
                    valid_tp = True
                    if type_pos == mt5.POSITION_TYPE_BUY and (opt_tp - current_price < stop_level_dist): valid_tp = False
                    if type_pos == mt5.POSITION_TYPE_SELL and (current_price - opt_tp < stop_level_dist): valid_tp = False
                    
                    if valid_tp and diff_tp > point * 30:
                        request['tp'] = opt_tp
                        changed = True
                        logger.info(f"AI/Stats 更新 TP: {tp:.2f} -> {opt_tp:.2f}")

                # 如果没有明确价格，但有 ATR 倍数建议 (兼容旧逻辑或备用)，则计算
                elif new_sl_multiplier > 0"""

new_content = pattern.sub(replacement, content, count=1)

if new_content == content:
    print("Pattern not found!")
else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File patched successfully.")
