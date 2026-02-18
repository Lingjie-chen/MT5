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

    def notify_trade(self, symbol, signal, price, sl, tp, lot, mode="N/A", win_rate="N/A", reason=""):
        """
        Format and send a trade notification.
        """
        icon = "🟢" if signal.lower() == 'buy' else "🔴"
        msg = (
            f"{icon} *Trade Executed*\n"
            f"Symbol: `{symbol}`\n"
            f"Action: *{signal.upper()}*\n"
            f"Mode: `{mode}`\n"
            f"Price: `{price}`\n"
            f"Lot: `{lot}`\n"
            f"SL: `{sl}`\n"
            f"TP/Basket: `{tp}`\n"
            f"Win Rate: `{win_rate}`\n"
            f"Reason: _{reason}_"
        )
        return self.send_message(msg)

    def notify_grid_deployment(self, symbol, count, trend, start_price, basket_tp=None, planned_count=None, skipped_count=None, failed_count=None, first_issue=None):
        """
        Notify about grid deployment.
        """
        tp_text = f"`${basket_tp}`" if basket_tp else "N/A"
        planned_text = f"`{planned_count}`" if planned_count is not None else "N/A"
        skipped_text = f"`{skipped_count}`" if skipped_count is not None else "N/A"
        failed_text = f"`{failed_count}`" if failed_count is not None else "N/A"
        issue_line = f"\nFirst Issue: `{first_issue}`" if first_issue else ""
        msg = (
            f"🕸 *Grid Deployed*\n"
            f"Symbol: `{symbol}`\n"
            f"Trend: *{trend.upper()}*\n"
            f"Orders Placed: `{count}`\n"
            f"Orders Planned: {planned_text}\n"
            f"Skipped: {skipped_text}\n"
            f"Failed: {failed_text}\n"
            f"Start Price: `{start_price}`\n"
            f"Basket TP: {tp_text}"
            f"{issue_line}"
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

    def notify_llm_analysis(self, symbol, mode, decision, reason, context_summary):
        """
        Notify about LLM analysis results (e.g., Grid Strategy Go/No-Go).
        """
        icon = "🧠"
        status_icon = "✅" if decision in ["deploy_grid", "buy", "sell"] else "⏸️"
        
        msg = (
            f"{icon} *LLM Analysis: {mode}*\n"
            f"Symbol: `{symbol}`\n"
            f"Decision: {status_icon} *{decision.upper()}*\n"
            f"Reasoning: _{reason}_\n"
            f"Context: `{context_summary}`"
        )
        return self.send_message(msg)

    def notify_info(self, title, message):
        """
        Notify about general info/status updates.
        """
        msg = (
            f"ℹ️ *{title}*\n"
            f"{message}"
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
