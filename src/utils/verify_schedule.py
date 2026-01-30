import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, time
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from trading_bot.main import SymbolTrader

class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader(symbol="ETHUSD")
        
    def check_time(self, weekday, hour, minute):
        # weekday: 0=Mon, ..., 5=Sat, 6=Sun
        # We mock datetime.now() to return a specific time
        # We need to construct a datetime object with the correct weekday
        # Let's pick a known date. Jan 1, 2024 was Monday.
        # Mon: Jan 1, Tue: Jan 2 ... Sat: Jan 6, Sun: Jan 7
        
        day_offset = weekday
        mock_date = datetime(2024, 1, 1 + day_offset, hour, minute)
        
        with patch('trading_bot.main.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_date
            return self.bot.check_trading_schedule()

    def test_ethusd_schedule(self):
        # 1. Saturday (Weekday 5)
        self.assertFalse(self.check_time(5, 7, 59), "Sat 07:59 should be closed")
        self.assertTrue(self.check_time(5, 8, 0), "Sat 08:00 should be open")
        self.assertTrue(self.check_time(5, 23, 59), "Sat 23:59 should be open")
        
        # 2. Sunday (Weekday 6)
        self.assertTrue(self.check_time(6, 0, 0), "Sun 00:00 should be open")
        self.assertTrue(self.check_time(6, 12, 0), "Sun 12:00 should be open")
        
        # 3. Monday (Weekday 0)
        self.assertTrue(self.check_time(0, 6, 29), "Mon 06:29 should be open")
        self.assertFalse(self.check_time(0, 6, 31), "Mon 06:31 should be closed")
        self.assertFalse(self.check_time(0, 12, 0), "Mon 12:00 should be closed")
        
        # 4. Tuesday (Weekday 1)
        self.assertFalse(self.check_time(1, 12, 0), "Tue 12:00 should be closed")

if __name__ == '__main__':
    unittest.main()
