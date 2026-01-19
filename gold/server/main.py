from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os

from . import models, schemas
from .models import SessionLocal, init_db

app = FastAPI(title="Quant Trading Bot Server")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Key Auth
API_KEY = os.getenv("SERVER_API_KEY", "your_secure_api_key_here")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.on_event("startup")
def on_startup():
    init_db()

# --- TRADES ---
@app.post("/api/trades", dependencies=[Depends(verify_api_key)])
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    db_trade = models.Trade(**trade.dict())
    # Upsert logic (simplified: merge)
    existing = db.query(models.Trade).filter(models.Trade.ticket == trade.ticket).first()
    if existing:
        for key, value in trade.dict().items():
            setattr(existing, key, value)
    else:
        db.add(db_trade)
    db.commit()
    return {"status": "ok"}

@app.post("/api/trades/update", dependencies=[Depends(verify_api_key)])
def update_trade(update: schemas.TradeUpdate, db: Session = Depends(get_db)):
    db_trade = db.query(models.Trade).filter(models.Trade.ticket == update.ticket).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    db_trade.close_price = update.close_price
    db_trade.close_time = update.close_time
    db_trade.profit = update.profit
    db_trade.mfe = update.mfe
    db_trade.mae = update.mae
    db_trade.result = update.result
    
    db.commit()
    return {"status": "updated"}

@app.get("/api/trades", dependencies=[Depends(verify_api_key)])
def get_trades(limit: int = 100, symbol: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Trade)
    if symbol:
        query = query.filter(models.Trade.symbol == symbol)
    return query.order_by(models.Trade.time.desc()).limit(limit).all()

# --- SIGNALS ---
@app.post("/api/signals", dependencies=[Depends(verify_api_key)])
def create_signal(signal: schemas.SignalCreate, db: Session = Depends(get_db)):
    # Map schema to model
    db_signal = models.Signal(
        timestamp=signal.timestamp,
        symbol=signal.symbol,
        timeframe=signal.timeframe,
        signal=signal.final_signal,
        strength=signal.strength,
        source=signal.source,
        details=signal.details,
        chat_id=signal.chat_id
    )
    db.add(db_signal)
    db.commit()
    return {"status": "ok"}

# --- ACCOUNT METRICS ---
@app.post("/api/account_metrics", dependencies=[Depends(verify_api_key)])
def create_metric(metric: schemas.AccountMetricCreate, db: Session = Depends(get_db)):
    db_metric = models.AccountMetric(**metric.dict())
    db.add(db_metric)
    db.commit()
    return {"status": "ok"}

# --- MARKET DATA ---
@app.post("/api/market_data", dependencies=[Depends(verify_api_key)])
def create_market_data(data: schemas.MarketDataCreate, db: Session = Depends(get_db)):
    # Upsert logic for market data
    existing = db.query(models.MarketData).filter(
        models.MarketData.timestamp == data.timestamp,
        models.MarketData.symbol == data.symbol,
        models.MarketData.timeframe == data.timeframe
    ).first()
    
    if existing:
        existing.open = data.open
        existing.high = data.high
        existing.low = data.low
        existing.close = data.close
        existing.volume = data.volume
    else:
        db_data = models.MarketData(**data.dict())
        db.add(db_data)
    
    db.commit()
    return {"status": "ok"}

@app.post("/api/market_data/batch", dependencies=[Depends(verify_api_key)])
def create_market_data_batch(data_list: List[schemas.MarketDataCreate], db: Session = Depends(get_db)):
    # Simplified batch insert
    # In production, use bulk_insert_mappings for performance
    for data in data_list:
        existing = db.query(models.MarketData).filter(
            models.MarketData.timestamp == data.timestamp,
            models.MarketData.symbol == data.symbol,
            models.MarketData.timeframe == data.timeframe
        ).first()
        
        if existing:
            existing.open = data.open
            existing.high = data.high
            existing.low = data.low
            existing.close = data.close
            existing.volume = data.volume
        else:
            db_data = models.MarketData(**data.dict())
            db.add(db_data)
    
    db.commit()
    return {"status": "ok", "count": len(data_list)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
