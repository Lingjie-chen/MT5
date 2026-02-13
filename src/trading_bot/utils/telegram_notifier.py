import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("TelegramNotifier")

class TelegramNotifier:
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        if not self.token or not self.chat_id:
            logger.warning("Telegram configuration missing (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")
            self.enabled = False
        else:
            self.enabled = True

    def send_message(self, message):
        """
        Send a text message to the configured Telegram chat.
        """
        if not self.enabled:
            return False

        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.base_url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info("Telegram message sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def notify_trade(self, symbol, signal, price, sl, tp, lot, reason=""):
        """
        Format and send a trade notification.
        """
        icon = "🟢" if signal.lower() == 'buy' else "🔴"
        msg = (
            f"{icon} *Trade Executed*\n"
            f"Symbol: `{symbol}`\n"
            f"Action: *{signal.upper()}*\n"
            f"Price: `{price}`\n"
            f"Lot: `{lot}`\n"
            f"SL: `{sl}`\n"
            f"TP/Basket: `{tp}`\n"
            f"Reason: _{reason}_"
        )
        return self.send_message(msg)

    def notify_grid_deployment(self, symbol, count, trend, start_price):
        """
        Notify about grid deployment.
        """
        msg = (
            f"🕸 *Grid Deployed*\n"
            f"Symbol: `{symbol}`\n"
            f"Trend: *{trend.upper()}*\n"
            f"Orders: `{count}`\n"
            f"Start Price: `{start_price}`"
        )
        return self.send_message(msg)

    def notify_basket_close(self, symbol, side, profit, reason):
        """
        Notify about basket closure (TP/Lock).
        """
        icon = "💰" if profit > 0 else "🛡️"
        msg = (
            f"{icon} *Basket Closed*\n"
            f"Symbol: `{symbol}`\n"
            f"Side: *{side.upper()}*\n"
            f"Total Profit: `${profit:.2f}`\n"
            f"Reason: _{reason}_"
        )
        return self.send_message(msg)

    def notify_error(self, context, error_msg):
        """
        Notify about critical errors.
        """
        msg = (
            f"⚠️ *Critical Error*\n"
            f"Context: `{context}`\n"
            f"Error: `{error_msg}`"
        )
        return self.send_message(msg)
