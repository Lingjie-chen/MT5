import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("GetChatID")

TOKEN = "8253887074:AAE_o7hfEb6iJCZ2MdVIezOC_E0OnTCvCzY"

def get_chat_id():
    """
    Fetches the latest updates from the bot to find the Chat ID.
    User must have sent a message to the bot recently.
    """
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    logger.info(f"Checking for updates from bot: @GoldADX_bot...")
    logger.info("NOTE: Please send a message (e.g., /start) to the bot if you haven't already!")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            logger.error(f"Error from Telegram API: {data}")
            return
            
        updates = data.get("result", [])
        if not updates:
            logger.warning("No updates found. Please send a message to the bot first!")
            return

        # Get the latest chat ID
        last_update = updates[-1]
        chat = last_update.get("message", {}).get("chat", {})
        
        chat_id = chat.get("id")
        username = chat.get("username")
        first_name = chat.get("first_name")
        
        if chat_id:
            logger.info("\n✅ SUCCESS! Found Chat ID:")
            logger.info(f"Chat ID: {chat_id}")
            logger.info(f"User: {first_name} (@{username})")
            logger.info("\nPlease update your .env file with this TELEGRAM_CHAT_ID.")
        else:
            logger.warning("Could not extract chat ID from the latest update.")
            logger.info(f"Raw update data: {json.dumps(last_update, indent=2)}")

    except Exception as e:
        logger.error(f"Failed to connect to Telegram: {e}")

if __name__ == "__main__":
    get_chat_id()
