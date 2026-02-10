import sys
import os
import pytest
from decimal import Decimal

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from position_engine.calculator import PositionCalculator
from position_engine.models import TradeSignal, AssetType

class TestPositionCalculator:
    def setup_method(self):
        self.calculator = PositionCalculator()

    def test_calculate_forex_position(self):
        # 模拟 EURUSD 交易，账户 USD
        signal = TradeSignal(
            total_capital=Decimal("10000"),
            account_currency="USD",
            quote_currency="USD", # EURUSD quote is USD
            risk_per_trade_percent=Decimal("1.0"), # $100 Risk
            entry_price=Decimal("1.1000"),
            stop_loss_price=Decimal("1.0900"), # 100 pips diff (0.0100)
            asset_type=AssetType.FOREX,
            contract_size=Decimal("100000"),
            leverage=Decimal("100"),
            manual_exchange_rate=Decimal("1.0") # USD/USD
        )
        
        result = self.calculator.calculate(signal)
        
        # Risk Amount = 10000 * 0.01 = 100
        # Price Diff = 0.0100
        # Risk Per Lot = 0.0100 * 100000 * 1.0 = 1000
        # Position Size = 100 / 1000 = 0.1
        
        assert result.suggested_position_size == Decimal("0.10")
        assert result.risk_amount_account == Decimal("100.00")
        assert result.execution_msg == "Success"

    def test_calculate_gold_position(self):
        # 模拟 XAUUSD 交易
        signal = TradeSignal(
            total_capital=Decimal("5000"),
            account_currency="USD",
            quote_currency="USD",
            risk_per_trade_percent=Decimal("2.0"), # $100 Risk
            entry_price=Decimal("2000.00"),
            stop_loss_price=Decimal("1990.00"), # $10 diff
            asset_type=AssetType.FOREX, # CFD usually treated as Forex/CFD
            contract_size=Decimal("100"),
            leverage=Decimal("100"),
            manual_exchange_rate=Decimal("1.0")
        )
        
        result = self.calculator.calculate(signal)
        
        # Risk Amount = 5000 * 0.02 = 100
        # Price Diff = 10.0
        # Risk Per Lot = 10.0 * 100 * 1.0 = 1000
        # Position Size = 100 / 1000 = 0.1
        
        assert result.suggested_position_size == Decimal("0.10")

    def test_drawdown_limit(self):
        signal = TradeSignal(
            total_capital=Decimal("10000"),
            risk_per_trade_percent=Decimal("1.0"),
            entry_price=Decimal("1.0"),
            stop_loss_price=Decimal("0.9"),
            asset_type=AssetType.STOCK,
            current_drawdown_percent=Decimal("25.0"),
            max_allowed_drawdown_percent=Decimal("20.0")
        )
        
        result = self.calculator.calculate(signal)
        assert result.risk_level == "BLOCKED"
        assert "MAX DRAWDOWN" in result.execution_msg
