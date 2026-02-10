import MetaTrader5 as mt5
import logging
from decimal import Decimal
from .models import TradeSignal, AssetType
from .calculator import PositionCalculator

logger = logging.getLogger("RiskManager")

class MT5RiskManager:
    def __init__(self):
        self.calculator = PositionCalculator()
        
    def get_asset_type(self, path: str, symbol: str) -> AssetType:
        path = path.lower()
        if "crypto" in path: return AssetType.CRYPTO
        if "forex" in path: return AssetType.FOREX
        if "stock" in path: return AssetType.STOCK
        return AssetType.FUTURE

    def calculate_lot_size(self, symbol: str, signal_price: float, stop_loss: float, risk_percent: float = 1.0) -> float:
        account = mt5.account_info()
        if not account: return 0.0

        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info: return 0.0

        try:
            signal = TradeSignal(
                total_capital=Decimal(str(account.balance)),
                account_currency=account.currency,
                quote_currency=symbol_info.currency_profit,
                risk_per_trade_percent=Decimal(str(risk_percent)),
                entry_price=Decimal(str(signal_price)),
                stop_loss_price=Decimal(str(stop_loss)),
                asset_type=self.get_asset_type(symbol_info.path, symbol),
                contract_size=Decimal(str(symbol_info.trade_contract_size)),
                leverage=Decimal(str(account.leverage))
            )

            result = self.calculator.calculate(signal)
            
            if result.risk_level == "BLOCKED":
                logger.warning(f"Risk Blocked: {result.execution_msg}")
                return 0.0
            
            # 最小手数检查 
            if float(result.suggested_position_size) < symbol_info.volume_min:
                return 0.0

            return float(result.suggested_position_size)

        except Exception as e:
            logger.error(f"Calc Error: {e}")
            return 0.0
