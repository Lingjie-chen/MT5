import sys
import os
from decimal import Decimal

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from position_engine.calculator import PositionCalculator
    from position_engine.models import TradeSignal, AssetType
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_calculate_forex_position():
    print("Testing Forex Position Calculation...")
    calculator = PositionCalculator()
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
    
    result = calculator.calculate(signal)
    
    assert result.suggested_position_size == Decimal("0.10"), f"Expected 0.10, got {result.suggested_position_size}"
    assert result.risk_amount_account == Decimal("100.00"), f"Expected 100.00, got {result.risk_amount_account}"
    assert result.execution_msg == "Success", f"Expected Success, got {result.execution_msg}"
    print("Forex Position Calculation Passed!")

def test_calculate_gold_position():
    print("Testing Gold Position Calculation...")
    calculator = PositionCalculator()
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
    
    result = calculator.calculate(signal)
    
    assert result.suggested_position_size == Decimal("0.10"), f"Expected 0.10, got {result.suggested_position_size}"
    print("Gold Position Calculation Passed!")

if __name__ == "__main__":
    try:
        test_calculate_forex_position()
        test_calculate_gold_position()
        print("All Tests Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
