import os
import logging
import requests
import json
import threading
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
