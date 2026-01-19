from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TradeCreate(BaseModel):
    ticket: int
    symbol: str
    action: str
    volume: float
    price: float
    time: datetime
    result: Optional[str] = "OPEN"
    chat_id: Optional[str] = None

class TradeUpdate(BaseModel):
    ticket: int
    close_price: float
    close_time: datetime
    profit: float
    mfe: float
    mae: float
    result: str = "CLOSED"

class SignalCreate(BaseModel):
    symbol: str
    timeframe: str
    final_signal: str
    strength: float
    source: str
    details: Dict[str, Any]
    timestamp: datetime
    chat_id: Optional[str] = None

class AccountMetricCreate(BaseModel):
    timestamp: datetime
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    total_profit: float
    symbol_pnl: float
    chat_id: Optional[str] = None

class MarketDataCreate(BaseModel):
    timestamp: datetime
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
