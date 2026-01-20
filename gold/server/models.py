from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
# POSTGRES_URL format: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot")

# Windows Encoding Fix: Force libpq to use UTF-8
os.environ["PGCLIENTENCODING"] = "utf-8"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"

    ticket = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String, index=True)
    action = Column(String)
    volume = Column(Float)
    price = Column(Float)
    time = Column(DateTime)
    result = Column(String)
    close_price = Column(Float, nullable=True)
    close_time = Column(DateTime, nullable=True)
    profit = Column(Float, nullable=True)
    mfe = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    chat_id = Column(String, nullable=True)
    
class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    symbol = Column(String)
    timeframe = Column(String)
    signal = Column(String)
    strength = Column(Float)
    source = Column(String)
    details = Column(JSON)
    chat_id = Column(String, nullable=True)

class AccountMetric(Base):
    __tablename__ = "account_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    balance = Column(Float)
    equity = Column(Float)
    margin = Column(Float)
    free_margin = Column(Float)
    margin_level = Column(Float)
    total_profit = Column(Float)
    symbol_pnl = Column(Float)
    chat_id = Column(String, nullable=True)

class MarketData(Base):
    __tablename__ = "market_data"

    timestamp = Column(DateTime, primary_key=True)
    symbol = Column(String, primary_key=True)
    timeframe = Column(String, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

def init_db():
    Base.metadata.create_all(bind=engine)
