from decimal import Decimal, ROUND_FLOOR
from .models import TradeSignal, CalculationResult, AssetType
from .services import ExchangeRateService

class PositionCalculator:
    def __init__(self):
        self.rate_service = ExchangeRateService()

    def calculate(self, signal: TradeSignal) -> CalculationResult:
        # 1. 熔断检查
        if signal.current_drawdown_percent >= signal.max_allowed_drawdown_percent:
            return self._zero_result(signal, "MAX DRAWDOWN LIMIT REACHED")

        # 2. 获取汇率
        try:
            if signal.manual_exchange_rate:
                exchange_rate = signal.manual_exchange_rate
            else:
                exchange_rate = self.rate_service.get_realtime_rate(
                    signal.quote_currency, signal.account_currency
                )
        except Exception as e:
            return self._zero_result(signal, f"Rate Error: {str(e)}")

        # 3. 计算账户本位币允许的风险额
        risk_amt_acc = signal.total_capital * (signal.risk_per_trade_percent / Decimal("100"))
        
        # 4. 计算单手合约风险 (转换为账户本位币)
        # 公式: |Entry - SL| * ContractSize * ExchangeRate
        price_diff = abs(signal.entry_price - signal.stop_loss_price)
        risk_per_unit_acc = price_diff * signal.contract_size * exchange_rate
        
        if risk_per_unit_acc == 0:
            return self._zero_result(signal, "Invalid SL Distance")

        # 5. 理论仓位
        raw_position = risk_amt_acc / risk_per_unit_acc

        # 6. 保证金与杠杆检查
        position_val_acc = raw_position * signal.entry_price * signal.contract_size * exchange_rate
        required_margin = position_val_acc / signal.leverage

        risk_level = "NORMAL"
        if required_margin > signal.total_capital:
            # 降级仓位
            raw_position = (signal.total_capital * signal.leverage) / \
                           (signal.entry_price * signal.contract_size * exchange_rate)
            risk_level = "HIGH (Margin Constraint)"

        # 7. 规格取整
        final_size = self._round_position(raw_position, signal.asset_type)

        return CalculationResult(
            suggested_position_size=final_size,
            position_value_quote=(final_size * signal.entry_price * signal.contract_size).quantize(Decimal("0.01")),
            risk_amount_account=(final_size * risk_per_unit_acc).quantize(Decimal("0.01")),
            required_margin_account=(final_size * signal.entry_price * signal.contract_size * exchange_rate / signal.leverage).quantize(Decimal("0.01")),
            exchange_rate_used=exchange_rate.quantize(Decimal("0.000001")),
            risk_level=risk_level,
            execution_msg="Success"
        )

    def _round_position(self, size: Decimal, asset_type: AssetType) -> Decimal:
        if asset_type == AssetType.STOCK or asset_type == AssetType.FUTURE:
            return size.quantize(Decimal("1"), rounding=ROUND_FLOOR)
        elif asset_type == AssetType.FOREX:
            return size.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
        elif asset_type == AssetType.CRYPTO:
            return size.quantize(Decimal("0.0001"), rounding=ROUND_FLOOR)
        return size

    def _zero_result(self, signal, msg) -> CalculationResult:
        # (简化版，返回全0对象)
        return CalculationResult(
            suggested_position_size=Decimal("0"), position_value_quote=Decimal("0"),
            risk_amount_account=Decimal("0"), required_margin_account=Decimal("0"),
            exchange_rate_used=Decimal("0"), risk_level="BLOCKED", execution_msg=msg
        )
