
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

# Mock MetaTrader5 before importing modules that use it
mock_mt5 = MagicMock()
sys.modules['MetaTrader5'] = mock_mt5

# Now import the modules
from position_engine.mt5_adapter import MT5RiskManager
from position_engine.models import TradeSignal

class TestQuantumIntegration(unittest.TestCase):
    def setUp(self):
        self.risk_manager = MT5RiskManager()
        
        # Mock mt5.account_info
        self.mock_account = MagicMock()
        self.mock_account.balance = 10000.0
        self.mock_account.currency = "USD"
        self.mock_account.leverage = 100
        mock_mt5.account_info.return_value = self.mock_account
        
        # Mock mt5.symbol_info
        self.mock_symbol_info = MagicMock()
        self.mock_symbol_info.currency_profit = "USD"
        self.mock_symbol_info.trade_contract_size = 100.0
        self.mock_symbol_info.path = "Forex/XAUUSD"
        self.mock_symbol_info.trade_tick_value = 1.0
        self.mock_symbol_info.trade_tick_size = 0.01
        self.mock_symbol_info.volume_min = 0.01
        mock_mt5.symbol_info.return_value = self.mock_symbol_info

    def test_calculate_lot_size_tier1(self):
        """Test conservative risk tier (0.5%)"""
        symbol = "XAUUSD"
        signal_price = 2000.0
        sl_price = 1995.0 # $5 distance
        risk_percent = 0.5 # 0.5% of $10000 = $50
        
        # Contract Size = 100
        # Loss per lot = $5 * 100 = $500
        # Expected Lots = $50 / $500 = 0.10
        
        lot = self.risk_manager.calculate_lot_size(symbol, signal_price, sl_price, risk_percent)
        
        print(f"\n[Test Tier 1] Risk: {risk_percent}%, Balance: ${self.mock_account.balance}")
        print(f"Signal: {signal_price}, SL: {sl_price}, Dist: {abs(signal_price-sl_price)}")
        print(f"Calculated Lot: {lot}")
        
        self.assertAlmostEqual(lot, 0.10)

    def test_calculate_lot_size_tier3(self):
        """Test aggressive risk tier (2.0%)"""
        symbol = "XAUUSD"
        signal_price = 2000.0
        sl_price = 1996.0 # $4 distance
        risk_percent = 2.0 # 2% of $10000 = $200
        
        # Loss per lot = $4 * 100 = $400
        # Expected Lots = $200 / $400 = 0.50
        
        lot = self.risk_manager.calculate_lot_size(symbol, signal_price, sl_price, risk_percent)
        
        print(f"\n[Test Tier 3] Risk: {risk_percent}%, Balance: ${self.mock_account.balance}")
        print(f"Signal: {signal_price}, SL: {sl_price}, Dist: {abs(signal_price-sl_price)}")
        print(f"Calculated Lot: {lot}")
        
        self.assertAlmostEqual(lot, 0.50)

    def test_main_logic_simulation(self):
        """Simulate the logic block in main.py"""
        print("\n[Test Main Logic Simulation]")
        
        # Mock LLM decision
        llm_decision = {
            "action": "buy",
            "risk_metrics": {
                "recommended_risk_percent": 1.5,
                "risk_rationale": "Good setup"
            },
            "position_size": 0.01 # This should be ignored/overridden
        }
        
        orb_signal = {'price': 2000.0, 'signal': 'buy'}
        smart_sl = 1990.0 # $10 distance
        
        # Logic from main.py
        try:
            risk_metrics = llm_decision.get('risk_metrics', {})
            recommended_risk = float(risk_metrics.get('recommended_risk_percent', 1.0))
            
            # 1.5% of 10000 = $150
            # Loss per lot = 10 * 100 = $1000
            # Expected Lot = 0.15
            
            calc_lot = self.risk_manager.calculate_lot_size(
                "XAUUSD", 
                orb_signal['price'], 
                smart_sl, 
                risk_percent=recommended_risk
            )
            
            print(f"LLM Risk: {recommended_risk}%")
            print(f"Calculated Lot: {calc_lot}")
            
            if calc_lot <= 0:
                print("Rejected")
            else:
                lot_size = calc_lot
                
            self.assertAlmostEqual(lot_size, 0.15)
            self.assertNotEqual(lot_size, llm_decision['position_size'])
            
        except Exception as e:
            self.fail(f"Logic failed: {e}")

if __name__ == '__main__':
    unittest.main()
