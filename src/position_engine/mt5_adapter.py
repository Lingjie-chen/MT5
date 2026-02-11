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
                logger.warning(f"Calculated lot {result.suggested_position_size} < Min Volume {symbol_info.volume_min}. Risk budget too low for this SL distance.")
                # Fallback: 如果计算结果极小但未被 BLOCKED，且在一定容差范围内，强制返回最小手数?
                # 或者直接返回 0.0 让上层决定
                # [Optimization] 如果计算结果 > 0 但小于 min，尝试返回 min 并警告风险超标?
                # 不，严格风控，返回 0.0
                return 0.0

            return float(result.suggested_position_size)

        except Exception as e:
            # 兼容性处理：如果 Decimal 转换失败，尝试使用 float 运算的简易版
            try:
                logger.warning(f"Quantum Engine failed ({e}), switching to Simple Fallback.")
                balance = account.balance
                risk_amt = balance * (risk_percent / 100.0)
                dist = abs(signal_price - stop_loss)
                if dist == 0: return 0.0
                
                tick_value = symbol_info.trade_tick_value
                tick_size = symbol_info.trade_tick_size
                
                # Loss per lot = (Dist / TickSize) * TickValue
                loss_per_lot = (dist / tick_size) * tick_value
                
                if loss_per_lot <= 0: return 0.0
                
                lot = risk_amt / loss_per_lot
                lot = max(symbol_info.volume_min, round(lot, 2))
                return lot
            except Exception as e2:
                logger.error(f"Fallback Calc Error: {e2}")
                return 0.0
