
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime
import sys
import os

# Adjust path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from trading_bot.utils.remote_storage import RemoteStorage

class TestRemoteStorageFix(unittest.TestCase):
    def setUp(self):
        # Mock env vars
        with patch.dict(os.environ, {"POSTGRES_API_URL": "http://test.com", "POSTGRES_API_KEY": "123", "TELEGRAM_CHAT_ID": "user123"}):
            self.storage = RemoteStorage()
            
    @patch('requests.post')
    def test_save_market_data_batch_payload(self, mock_post):
        # Create a dummy dataframe
        data = {
            'open': [1.1, 1.2],
            'high': [1.2, 1.3],
            'low': [1.0, 1.1],
            'close': [1.15, 1.25],
            'volume': [100, 200]
        }
        index = [datetime(2023, 1, 1, 10, 0), datetime(2023, 1, 1, 10, 5)]
        df = pd.DataFrame(data, index=index)
        
        # Call the method
        # It runs in a thread, so we need to wait or extract the inner task
        # But for testing, we can just call the task function if we can access it, 
        # or mock threading to run immediately?
        # Simpler: just extract the logic we changed into a helper or modify the test to mock threading.Thread to run synchronously.
        
        with patch('threading.Thread') as mock_thread:
            # Configure mock_thread to run the target immediately
            def side_effect(target, daemon):
                target()
                return MagicMock()
            
            mock_thread.side_effect = side_effect
            
            self.storage.save_market_data_batch(df, "EURUSD", "M5")
            
            # Verify requests.post was called
            self.assertTrue(mock_post.called)
            
            # Inspect the payload
            args, kwargs = mock_post.call_args
            payload = kwargs['json']
            
            print(f"Payload sent: {payload}")
            
            # Check if chat_id is present
            self.assertEqual(len(payload), 2)
            self.assertEqual(payload[0]['chat_id'], "user123")
            self.assertEqual(payload[1]['chat_id'], "user123")
            self.assertEqual(payload[0]['symbol'], "EURUSD")

if __name__ == '__main__':
    unittest.main()
