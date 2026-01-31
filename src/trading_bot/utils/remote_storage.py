import os
import logging
import requests
import json
import threading
import math
from datetime import datetime

logger = logging.getLogger("RemoteStorage")

class RemoteStorage:
    """
    Handles asynchronous data transmission to a remote PostgreSQL backend via HTTP.
    Uses a background thread to prevent blocking the main trading loop.
    """
    def __init__(self):
        self.api_url = os.getenv("POSTGRES_API_URL", "")
        self.api_key = os.getenv("POSTGRES_API_KEY", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")  # Used to associate data with user
        self.enabled = bool(self.api_url)
        
        if self.enabled:
            logger.info(f"Remote Storage Enabled. Target: {self.api_url}")
        else:
            logger.info("Remote Storage Disabled (POSTGRES_API_URL not set)")

    def _send_payload(self, endpoint, data):
        """Internal method to send data via HTTP POST"""
        if not self.enabled:
            return

        def task():
            try:
                url = f"{self.api_url}/{endpoint}"
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                }
                
                # Enrich data with metadata
                payload = data.copy()
                payload['chat_id'] = self.chat_id
                payload['timestamp'] = payload.get('timestamp', datetime.now().isoformat())
                
                # Convert datetime objects to string if needed
                # (requests.json encoder might handle standard types, but safer to pre-process)
                payload = self._serialize_dates(payload)
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                if response.status_code not in [200, 201]:
                    logger.warning(f"Failed to send to {endpoint}: {response.status_code} {response.text}")
            except Exception as e:
                logger.error(f"Error sending to {endpoint}: {e}")

        # Run in background thread
        threading.Thread(target=task, daemon=True).start()

    def _serialize_dates(self, data):
        """Recursively convert datetime objects to ISO format strings"""
        if isinstance(data, dict):
            return {k: self._serialize_dates(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_dates(v) for v in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        return data

    def save_trade(self, trade_data):
        """Send trade record to remote DB"""
        self._send_payload("trades", trade_data)

    def save_signal(self, signal_data):
        """Send signal record to remote DB"""
        self._send_payload("signals", signal_data)

    def save_account_metrics(self, metrics):
        """Send account metrics to remote DB"""
        self._send_payload("account_metrics", metrics)

    def update_trade_performance(self, ticket, close_data):
        """Send trade update (close info)"""
        data = close_data.copy()
        data['ticket'] = ticket
        self._send_payload("trades/update", data)

    def save_market_data_batch(self, df, symbol, timeframe):
        """Send a batch of market data (candles) to remote DB"""
        if not self.enabled or df.empty:
            return

        def task():
            try:
                endpoint = "market_data/batch"
                url = f"{self.api_url}/{endpoint}"
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                }
                
                # Convert DataFrame to list of dicts
                # Assuming df index is timestamp
                records = []
                for index, row in df.iterrows():
                    o = float(row['open'])
                    h = float(row['high'])
                    l = float(row['low'])
                    c = float(row['close'])
                    v = float(row['volume'])
                    
                    record = {
                        "chat_id": self.chat_id,  # [FIX] Inject chat_id for multi-tenancy support
                        "timestamp": index.isoformat() if isinstance(index, datetime) else str(index),
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "open": None if math.isnan(o) else o,
                        "high": None if math.isnan(h) else h,
                        "low": None if math.isnan(l) else l,
                        "close": None if math.isnan(c) else c,
                        "volume": None if math.isnan(v) else v
                    }
                    records.append(record)
                
                # Split into chunks if too large (e.g., 100 records per request)
                chunk_size = 100
                for i in range(0, len(records), chunk_size):
                    chunk = records[i:i + chunk_size]
                    response = requests.post(url, json=chunk, headers=headers, timeout=20)
                    if response.status_code not in [200, 201]:
                         # [FIX] Log more details for 500 errors
                         logger.warning(f"Failed to send market data batch: {response.status_code} - {response.text[:500]}")
            except Exception as e:
                logger.error(f"Error sending market data batch: {e}")

        threading.Thread(target=task, daemon=True).start()

    def get_trades(self, limit=100, symbol=None):
        """Retrieve trades from remote DB (Synchronous call)"""
        if not self.enabled:
            return []
            
        try:
            endpoint = "trades"
            url = f"{self.api_url}/{endpoint}"
            headers = {"X-API-Key": self.api_key}
            
            params = {}
            if self.chat_id:
                params['chat_id'] = self.chat_id # [FIX] Include chat_id for retrieval
                
            if limit is not None:
                params['limit'] = limit
            else:
                # If limit is explicitly None, try to fetch a large number to get "all"
                # (assuming backend might default to a small page size if parameter is missing)
                params['limit'] = 100000
                
            if symbol:
                params['symbol'] = symbol
                
            response = requests.get(url, headers=headers, params=params, timeout=30) # Increased timeout for large data
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get trades: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
