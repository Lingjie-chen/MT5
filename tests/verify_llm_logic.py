
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.getcwd())

# --- Mock MetaTrader5 BEFORE importing main ---
mock_mt5 = MagicMock()
sys.modules['MetaTrader5'] = mock_mt5
sys.modules['pymt5adapter'] = MagicMock()

# Setup MT5 Constants
mock_mt5.TIMEFRAME_M15 = 15
mock_mt5.ORDER_TYPE_BUY = 0
mock_mt5.ORDER_TYPE_SELL = 1
mock_mt5.POSITION_TYPE_BUY = 0
mock_mt5.POSITION_TYPE_SELL = 1
mock_mt5.TRADE_ACTION_DEAL = 1
mock_mt5.ORDER_TIME_GTC = 0
mock_mt5.ORDER_FILLING_FOK = 0
mock_mt5.TRADE_RETCODE_DONE = 10009
mock_mt5.ORDER_FILLING_RETURN = 2
mock_mt5.ORDER_FILLING_IOC = 1

# Setup Mock Data
mock_account = MagicMock()
mock_account.balance = 10000.0
mock_account.equity = 10000.0
mock_account.margin_free = 9000.0 # Plenty of margin
mock_account.leverage = 100
mock_mt5.account_info.return_value = mock_account

mock_symbol_info = MagicMock()
mock_symbol_info.volume_min = 0.01
mock_symbol_info.volume_max = 100.0
mock_symbol_info.volume_step = 0.01
mock_symbol_info.point = 0.00001
mock_symbol_info.digits = 5
mock_symbol_info.trade_tick_value = 1.0
mock_symbol_info.trade_tick_size = 0.00001
mock_symbol_info.filling_mode = 1
mock_mt5.symbol_info.return_value = mock_symbol_info

mock_tick = MagicMock()
mock_tick.ask = 1.1000
mock_tick.bid = 1.0999
mock_mt5.symbol_info_tick.return_value = mock_tick

# Mock Margin Calc (Return valid margin requirement)
mock_mt5.order_calc_margin.return_value = 250.0 # 0.5 lots margin

# Mock Order Send Success
mock_result = MagicMock()
mock_result.retcode = 10009
mock_result.order = 888888
mock_mt5.order_send.return_value = mock_result

# Mock Positions (Empty)
mock_mt5.positions_get.return_value = []

# --- Import Class to Test ---
try:
    from src.trading_bot.main import SymbolTrader
except ImportError:
    print("Error importing SymbolTrader. Make sure you are in the project root.")
    sys.exit(1)

# --- Subclass to Isolate Logic ---
class LogicTester(SymbolTrader):
    def __init__(self):
        # Bypass standard init
        self.symbol = "EURUSD"
        self.timeframe = 15
        self.magic_number = 123456
        self.lot_size = 0.01
        self.latest_strategy = {}
        
        # Mock Dependencies
        self.db_manager = MagicMock()
        self.db_manager.get_performance_metrics.return_value = {
            'win_rate': 0.5, 'profit_factor': 1.2, 'consecutive_losses': 0
        }
        self.db_manager.get_trade_performance_stats.return_value = {}
        
        # Mock Logger to avoid clutter
        # self.logger = MagicMock() 

    def check_account_safety(self, close_if_critical=True):
        return True, "Safe"

    def send_telegram_message(self, msg):
        print(f"   [Telegram] {msg.replace(chr(10), ' ')}")

# --- Run Tests ---
print(">>> 开始逻辑验证测试 (Logic Verification Test) <<<\n")

trader = LogicTester()

# Scenario: LLM wants 0.5 Lots with specific SL/TP
print("场景 1: 大模型建议 0.5 手, 明确 SL=1.0950, TP=1.1100")
trader.latest_strategy = {
    'action': 'buy',
    'position_size': 0.5,  # <-- 重点验证对象
    'sl': 1.0950,          # <-- 重点验证对象
    'tp': 1.1100,          # <-- 重点验证对象
    'exit_conditions': {'sl_price': 1.0950}
}

# 1. Test Lot Calculation
print("1. 测试仓位计算 (calculate_dynamic_lot)...")
calculated_lot = trader.calculate_dynamic_lot(strength=85)
print(f"   -> 计算结果: {calculated_lot} Lots")

if calculated_lot == 0.5:
    print("   [PASS] 成功采纳大模型建议仓位 (0.5)")
else:
    print(f"   [FAIL] 仓位计算错误. 期望 0.5, 实际 {calculated_lot}")

# 2. Test Execution
print("\n2. 测试下单执行 (execute_trade)...")
trader.execute_trade(
    signal='buy',
    strength=85,
    sl_tp_params={'sl_price': 1.0950, 'tp_price': 1.1100},
    entry_params={'action': 'buy'},
    suggested_lot=calculated_lot
)

# Verify Order Sent
call_args = mock_mt5.order_send.call_args
if call_args:
    req = call_args[0][0]
    print("   -> 发送到 MT5 的订单参数:")
    print(f"      Action: {req['action']} (DEAL)")
    print(f"      Symbol: {req['symbol']}")
    print(f"      Volume: {req['volume']} (Expect 0.5)")
    print(f"      Price:  {req['price']}")
    print(f"      SL:     {req['sl']} (Expect 1.0950)")
    print(f"      TP:     {req['tp']} (Expect 1.1100)")
    
    # Assertions
    failures = []
    if req['volume'] != 0.5: failures.append(f"Volume mismatch ({req['volume']})")
    if req['sl'] != 1.0950: failures.append(f"SL mismatch ({req['sl']})")
    if req['tp'] != 1.1100: failures.append(f"TP mismatch ({req['tp']})")
    
    if not failures:
        print("   [PASS] 订单参数完全匹配大模型指令！")
    else:
        print(f"   [FAIL] 参数不匹配: {', '.join(failures)}")
else:
    print("   [FAIL] 未调用 order_send")

print("\n>>> 测试完成 <<<")
