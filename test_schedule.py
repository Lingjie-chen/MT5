
import logging
from datetime import datetime, time

# Mock logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBot:
    def __init__(self, symbol):
        self.symbol = symbol

    def check_trading_schedule(self, mock_now):
        """
        Check if trading is allowed based on the schedule and symbol.
        Rules:
        - ETHUSD: Weekend (Sat-Sun) + Monday < 07:00.
        - GOLD/XAUUSD/EURUSD: Monday >= 06:30 to Saturday 00:00.
        """
        now = mock_now
        weekday = now.weekday() # 0=Mon, 6=Sun
        current_time = now.time()
        
        symbol_upper = self.symbol.upper()
        
        # Crypto Rules (ETHUSD)
        if "ETH" in symbol_upper:
            is_weekend = weekday >= 5
            is_monday_morning = (weekday == 0 and current_time.hour < 7)
            
            if is_weekend or is_monday_morning:
                return True
            else:
                return False
                
        # Forex/Metal Rules (GOLD, EURUSD)
        if "GOLD" in symbol_upper or "XAU" in symbol_upper or "EUR" in symbol_upper:
            # 周一: 需 06:30 之后
            if weekday == 0:
                if (current_time.hour > 6) or (current_time.hour == 6 and current_time.minute >= 30):
                    return True
                else:
                    return False
            
            # 周二(1) - 周五(4): 全天允许
            elif 1 <= weekday <= 4:
                return True
                
            # 周六(5) - 周日(6): 禁止
            else:
                return False
                
        return True

def test_schedule():
    # Test Cases
    test_cases = [
        # ETHUSD Tests
        ("ETHUSD", datetime(2024, 1, 27, 12, 0), True, "Saturday Noon"),
        ("ETHUSD", datetime(2024, 1, 28, 12, 0), True, "Sunday Noon"),
        ("ETHUSD", datetime(2024, 1, 29, 6, 59), True, "Monday 6:59 AM"),
        ("ETHUSD", datetime(2024, 1, 29, 7, 0), False, "Monday 7:00 AM"),
        ("ETHUSD", datetime(2024, 1, 30, 12, 0), False, "Tuesday Noon"),
        
        # GOLD Tests (Forex)
        ("GOLD", datetime(2024, 1, 29, 6, 29), False, "Monday 6:29 AM"),
        ("GOLD", datetime(2024, 1, 29, 6, 30), True, "Monday 6:30 AM"),
        ("GOLD", datetime(2024, 1, 30, 12, 0), True, "Tuesday Noon"),
        ("GOLD", datetime(2024, 2, 2, 23, 59), True, "Friday 23:59"),
        ("GOLD", datetime(2024, 2, 3, 0, 0), False, "Saturday 00:00 (Midnight)"),
        ("GOLD", datetime(2024, 2, 3, 12, 0), False, "Saturday Noon"),
    ]
    
    for symbol, dt, expected, desc in test_cases:
        bot = MockBot(symbol)
        result = bot.check_trading_schedule(dt)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] {symbol} at {desc} ({dt}): Expected {expected}, Got {result}")

if __name__ == "__main__":
    test_schedule()
