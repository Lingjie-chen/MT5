import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from trading_bot.main import SymbolTrader, mt5

class TestPositionSizing(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader(symbol="GOLD")
        self.bot.symbol = "GOLD"
        
    @patch('trading_bot.main.mt5')
    def test_calculate_dynamic_lot_llm(self, mock_mt5):
        """测试大模型建议仓位的有效性和资金检查"""
        
        # 1. 模拟账户资金信息 (Balance $5000, Free Margin $4000)
        mock_account = MagicMock()
        mock_account.balance = 5000.0
        mock_account.equity = 5000.0
        mock_account.margin_free = 4000.0
        mock_account.leverage = 100
        mock_mt5.account_info.return_value = mock_account
        
        # 2. 模拟品种信息 (GOLD)
        mock_symbol_info = MagicMock()
        mock_symbol_info.volume_step = 0.01
        mock_symbol_info.volume_min = 0.01
        mock_symbol_info.volume_max = 100.0
        mock_symbol_info.trade_tick_value = 1.0
        mock_mt5.symbol_info.return_value = mock_symbol_info
        
        # 3. 模拟报价
        mock_tick = MagicMock()
        mock_tick.bid = 2000.0
        mock_tick.ask = 2000.5
        mock_mt5.symbol_info_tick.return_value = mock_tick
        
        # Case A: LLM 建议 0.1 手，资金充足 -> 应该采纳 0.1
        self.bot.latest_strategy = {'position_size': 0.1, 'action': 'buy'}
        mock_mt5.order_calc_margin.return_value = 200.0 # 需要 $200 保证金
        
        lot = self.bot.calculate_dynamic_lot(strength=80)
        self.assertEqual(lot, 0.1, "Funds sufficient, should accept LLM lot 0.1")
        
        # Case B: LLM 建议 5.0 手，资金不足 -> 应该降级
        self.bot.latest_strategy = {'position_size': 5.0, 'action': 'buy'}
        # 假设 5.0 手需要 $5000 保证金，而可用只有 $4000 (safe $3800)
        mock_mt5.order_calc_margin.return_value = 5000.0 
        
        # 期望逻辑：
        # Margin Per Lot = 5000 / 5.0 = 1000
        # Safe Margin = 4000 * 0.95 = 3800
        # New Lot = 3800 / 1000 = 3.8
        
        lot = self.bot.calculate_dynamic_lot(strength=80)
        self.assertEqual(lot, 3.8, f"Funds insufficient, should downgrade to ~3.8, got {lot}")
        
        # Case C: LLM 建议极大仓位触发熔断保护 (Risk Cap)
        # 假设建议 10 手，保证金虽然够（假设极高杠杆），但 Risk > Equity * 25%
        # Risk Est = 10 * 500 * 1 = $5000 Risk. Equity = $5000. Max Risk = $1250.
        # 此时应触发熔断，拒绝 LLM 建议，回退到默认算法计算
        
        mock_account.margin_free = 100000.0 # 保证金无限
        mock_mt5.order_calc_margin.return_value = 1000.0
        
        self.bot.latest_strategy = {'position_size': 10.0, 'action': 'buy'}
        
        # 如果触发熔断，函数会跳过 return llm_lot，进入下方默认计算
        # [UPDATED] 现在代码会触发自动调整到安全仓位，而不是回退到默认计算
        # Risk Cap = $5000 * 0.25 = $1250
        # Safe Lot = 1250 / (500 * 1.0) = 2.5 Lots
        
        lot = self.bot.calculate_dynamic_lot(strength=80)
        self.assertEqual(lot, 2.5, f"Should auto-adjust risky lot to max safe limit. Expected 2.5, got {lot}")

if __name__ == '__main__':
    unittest.main()
