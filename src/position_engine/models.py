from enum import Enum
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class AssetType(str, Enum):
    STOCK = "STOCK"
    FUTURE = "FUTURE"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"

class TradeSignal(BaseModel):
    total_capital: Decimal = Field(..., gt=0, description="账户总资金")
    account_currency: str = Field(default="USD", min_length=3, max_length=3)
    quote_currency: str = Field(default="USD", min_length=3, max_length=3)
    
    risk_per_trade_percent: Decimal = Field(..., gt=0, le=100)
    entry_price: Decimal = Field(..., gt=0)
    stop_loss_price: Decimal = Field(..., gt=0)
    
    asset_type: AssetType
    contract_size: Decimal = Field(default=Decimal("1.0"))
    leverage: Decimal = Field(default=Decimal("1.0"), gt=0)
    
    current_drawdown_percent: Decimal = Field(default=Decimal("0.0"))
    max_allowed_drawdown_percent: Decimal = Field(default=Decimal("20.0"))
    
    manual_exchange_rate: Optional[Decimal] = Field(default=None)

    @field_validator('stop_loss_price')
    def validate_sl(cls, v, values):
        if 'entry_price' in values.data and v == values.data['entry_price']:
            raise ValueError("止损价格不能等于入场价格")
        return v
    
    @field_validator('account_currency', 'quote_currency')
    def upper_case_currency(cls, v):
        return v.upper()

class CalculationResult(BaseModel):
    suggested_position_size: Decimal
    position_value_quote: Decimal
    risk_amount_account: Decimal
    required_margin_account: Decimal
    exchange_rate_used: Decimal
    risk_level: str
    execution_msg: str
