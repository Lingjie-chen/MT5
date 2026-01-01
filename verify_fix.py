
import sys
import os
import unittest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np

# Mock dependencies
sys.modules['crypto.okx_data_processor'] = MagicMock()
sys.modules['crypto.ai_client_factory'] = MagicMock()
sys.modules['crypto.database_manager'] = MagicMock()
sys.modules['crypto.advanced_analysis'] = MagicMock()

# Mock specific classes
mock_processor = MagicMock()
# Return a valid DataFrame
df_mock = pd.DataFrame({
    'open': [100.0]*10, 'high': [105.0]*10, 'low': [95.0]*10, 'close': [102.0]*10, 'volume': [1000.0]*10
})
df_mock.name = MagicMock()
df_mock.name.timestamp.return_value = 1234567890

mock_processor.get_historical_data.return_value = df_mock
mock_processor.generate_features.return_value = df_mock

sys.modules['crypto.okx_data_processor'].OKXDataProcessor.return_value = mock_processor

# Import the bot (it will use the mocks)
# We need to set the path so it can import 'crypto'
sys.path.append(os.getcwd())

try:
    from crypto.trading_bot import CryptoTradingBot
    
    # Instantiate
    bot = CryptoTradingBot()
    
    # Mock internal components that might fail
    bot.crt_analyzer = MagicMock()
    bot.crt_analyzer.analyze.return_value = {'signal': 'neutral'}
    
    bot.price_model = MagicMock()
    bot.price_model.analyze.return_value = {'signal': 'neutral'}
    
    bot.tf_analyzer = MagicMock()
    bot.tf_analyzer.analyze.return_value = {'signal': 'neutral'}
    
    bot.mtf_analyzer = MagicMock()
    bot.mtf_analyzer.analyze.return_value = {'signal': 'neutral'}
    
    bot.advanced_adapter = MagicMock()
    bot.advanced_adapter.analyze_full.return_value = {'signal_info': {'signal': 'neutral'}}
    
    bot.matrix_ml = MagicMock()
    bot.matrix_ml.predict.return_value = {'signal': 'neutral'}
    
    bot.smc_analyzer = MagicMock()
    bot.smc_analyzer.analyze.return_value = {'signal': 'neutral'}
    
    bot.mfh_analyzer = MagicMock()
    bot.mfh_analyzer.predict.return_value = {'signal': 'neutral'}
    
    bot.deepseek_client = MagicMock()
    bot.deepseek_client.analyze_market_structure.return_value = {}
    
    bot.qwen_client = MagicMock()
    bot.qwen_client.optimize_strategy_logic.return_value = {'action': 'hold'}
    
    bot.db_manager = MagicMock()
    
    # Run analyze_market
    print("Running analyze_market()...")
    try:
        bot.analyze_market()
        print("analyze_market() finished successfully (no NameError).")
    except NameError as e:
        print(f"FAILED with NameError: {e}")
    except Exception as e:
        print(f"FAILED with other error: {e}")
        import traceback
        traceback.print_exc()

except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Setup failed: {e}")
