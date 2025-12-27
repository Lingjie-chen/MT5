import time
import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from .okx_data_processor import OKXDataProcessor
from .ai_client_factory import AIClientFactory
from .database_manager import DatabaseManager

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoTradingBot:
    def __init__(self, symbol='ETH/USDT', timeframe='M15', interval=3600):
        """
        Initialize the Crypto Trading Bot
        
        Args:
            symbol (str): Trading pair
            timeframe (str): Candle timeframe
            interval (int): Loop interval in seconds
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.interval = interval
        self.is_running = False
        
        # Initialize Data Processor
        self.data_processor = OKXDataProcessor()

        # Initialize Database Manager
        # Using a dedicated database file for Crypto strategy to keep it separate from Gold strategy
        self.db_manager = DatabaseManager(db_name='crypto_trading.db')
        
        # Initialize AI Clients
        self.ai_factory = AIClientFactory()
        self.deepseek_client = self.ai_factory.get_client('deepseek')
        self.qwen_client = self.ai_factory.get_client('qwen')
        
        if not self.deepseek_client or not self.qwen_client:
            logger.warning("AI Clients not fully initialized. Trading functionality may be limited.")
            
    def analyze_market(self):
        """Analyze market using DeepSeek"""
        logger.info(f"Fetching data for {self.symbol}...")
        df = self.data_processor.get_historical_data(self.symbol, self.timeframe, limit=100)
        
        if df.empty:
            logger.error("Failed to fetch historical data")
            return None, None
            
        # Generate features
        df = self.data_processor.generate_features(df)
        
        # Prepare data for AI analysis
        # We take the last few candles and latest indicators
        latest_data = df.iloc[-1].to_dict()
        recent_candles = df.iloc[-5:].reset_index().to_dict('records')
        
        market_data = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "current_price": latest_data.get('close'),
            "indicators": {
                "ema_fast": latest_data.get('ema_fast'),
                "ema_slow": latest_data.get('ema_slow'),
                "rsi": latest_data.get('rsi'),
                "atr": latest_data.get('atr'),
                "volatility": latest_data.get('volatility')
            },
            "recent_candles": recent_candles
        }
        
        logger.info("Requesting DeepSeek market structure analysis...")
        structure_analysis = self.deepseek_client.analyze_market_structure(market_data)
        logger.info(f"Market Structure Analysis: {structure_analysis.get('market_state')}")
        
        # Log analysis to database
        try:
            self.db_manager.log_analysis(
                symbol=self.symbol,
                market_state=structure_analysis.get('market_state'),
                structure_score=structure_analysis.get('structure_score'),
                ai_decision=None, # Will be updated after decision is made or just log analysis here
                raw_analysis=structure_analysis
            )
        except Exception as e:
            logger.error(f"Failed to log analysis to DB: {e}")
            
        return df, structure_analysis

    def make_decision(self, df, structure_analysis):
        """Make trading decision using Qwen"""
        if not self.qwen_client:
            logger.error("Qwen client not initialized")
            return None

        latest_data = df.iloc[-1].to_dict()
        
        # Get current balance
        balance = self.data_processor.get_account_balance('USDT')
        available_usdt = balance['free'] if balance else 0.0
        
        # Also get total equity (balance + unrealized PnL) to give AI a better picture
        total_equity = balance['total'] if balance else available_usdt
        
        logger.info(f"Current available USDT: {available_usdt}, Total Equity: {total_equity}")
        
        # Get current balance/positions (simplified)
        # In a real scenario, you'd fetch actual positions from OKX
        # Fetch actual positions to provide accurate context to AI
        try:
            positions = self.data_processor.exchange.fetch_positions([self.symbol])
            # Process positions for AI context
            formatted_positions = []
            for pos in positions:
                formatted_positions.append({
                    "symbol": pos['symbol'],
                    "side": pos['side'], # long or short
                    "contracts": pos['contracts'],
                    "size": pos['info'].get('sz', 0), # Position size in base currency or contracts
                    "notional": pos['notional'], # Position value in USDT
                    "leverage": pos['leverage'],
                    "unrealized_pnl": pos['unrealizedPnl'],
                    "margin_mode": pos['marginMode'],
                    "liquidation_price": pos['liquidationPrice']
                })
            current_positions = formatted_positions
            logger.info(f"Current Positions: {json.dumps(current_positions, default=str)}")
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            current_positions = [] 
        
        market_data = {
            "symbol": self.symbol,
            "price": latest_data.get('close'),
            "indicators": {
                "ema_fast": latest_data.get('ema_fast'),
                "ema_slow": latest_data.get('ema_slow'),
                "rsi": latest_data.get('rsi')
            },
            "account_info": {
                "available_usdt": available_usdt,
                "total_equity": total_equity
            }
        }
        
        logger.info("Requesting Qwen strategy optimization...")
        decision = self.qwen_client.optimize_strategy_logic(
            structure_analysis,
            market_data,
            current_positions=current_positions
        )
        
        return decision

    def execute_trade(self, decision):
        """Execute trade based on decision"""
        action = decision.get('action')
        rationale = decision.get('strategy_rationale', 'No rationale provided')
        
        # ... (Previous code) ...
        
        # Check if we need to update SL/TP for EXISTING positions (Hold logic)
        if action == 'hold':
            # Get current position info
            # We need to find the matching position for this symbol
            target_pos = None
            try:
                positions = self.data_processor.exchange.fetch_positions([self.symbol])
                if positions:
                    target_pos = positions[0] # Assuming one position per symbol mode
            except:
                pass
                
            if target_pos and float(target_pos['contracts']) > 0:
                exit_conditions = decision.get('exit_conditions', {})
                new_sl = exit_conditions.get('sl_price')
                new_tp = exit_conditions.get('tp_price')
                
                if new_sl or new_tp:
                    logger.info(f"Updating SL/TP for existing position: SL={new_sl}, TP={new_tp}")
                    
                    # Determine direction for SL order (opposite to position)
                    pos_side = target_pos['side'] # 'long' or 'short'
                    sl_tp_side = 'sell' if pos_side == 'long' else 'buy'
                    pos_amount = float(target_pos['contracts']) # Contracts amount
                    
                    # Cancel existing open orders (SL/TPs) to avoid stacking
                    self.data_processor.cancel_all_orders(self.symbol)
                    
                    # Place new SL/TP
                    self.data_processor.place_sl_tp_order(self.symbol, sl_tp_side, pos_amount, sl_price=new_sl, tp_price=new_tp)
            return

        logger.info(f"Strategy Decision: {action}")
        logger.info(f"Rationale: {rationale}")
        leverage = int(decision.get('leverage', 1))
        logger.info(f"Suggested Leverage: {leverage}x")
        
        # Determine trade volume based on available balance and model recommendation
        volume_percent = decision.get('position_size', 0.0)
        
        # Ensure volume_percent is within 0-1 range
        volume_percent = max(0.0, min(1.0, float(volume_percent)))
        
        logger.info(f"Model recommended position size: {volume_percent:.2%} of available funds")
        
        if volume_percent <= 0:
            logger.warning("Recommended position size is 0, skipping trade")
            return

        # Fetch latest balance
        balance = self.data_processor.get_account_balance('USDT')
        available_usdt = balance['free'] if balance else 0.0
        
        # Calculate target USDT amount
        target_usdt = available_usdt * volume_percent
        
        # Get current price
        current_price = self.data_processor.get_current_price(self.symbol)
        
        if not current_price:
            logger.error("Failed to get current price, skipping trade")
            return
            
        # Ensure price is float
        try:
            current_price = float(current_price)
        except ValueError:
             logger.error(f"Invalid price format: {current_price}")
             return

        # Calculate amount in base currency (e.g. ETH)
        # Reserve 1% for fees to be safe if going full allocation
        if volume_percent > 0.95:
             target_usdt = target_usdt * 0.99

        target_margin = target_usdt
        # Leverage is already defined at the beginning of the function
        leverage = int(decision.get('leverage', 1))
        
        target_position_value = target_margin * leverage

        # Amount = Position Value / Price
        # Ensure we use the leveraged position value
        amount_eth = target_position_value / current_price
        
        # Convert to contracts
        # OKX ETH/USDT Swap: 1 contract = 0.1 ETH
        contract_size = 0.1
        num_contracts = int(amount_eth / contract_size)
        
        logger.info(f"Volume Calculation: Available USDT={available_usdt}, Percent={volume_percent:.2%}, Margin={target_margin:.2f}, Leverage={leverage}x, Position Value={target_position_value:.2f}, Price={current_price}, Amount (ETH)={amount_eth:.6f}, Contracts={num_contracts}")
        
        # Minimum position value check (at least 1 contract)
        if num_contracts < 1:
            logger.warning(f"Calculated contracts ({num_contracts}) is less than 1, skipping")
            return

        # Prepare SL/TP params for OKX
        exit_conditions = decision.get('exit_conditions', {})
        sl_price = exit_conditions.get('sl_price')
        tp_price = exit_conditions.get('tp_price')
        
        order_params = {}
        if sl_price or tp_price:
            algo_order = {
                'attachAlgoClOrdId': f"algo_{int(time.time())}"
            }
            if tp_price:
                algo_order['tpTriggerPx'] = str(tp_price)
                algo_order['tpOrdPx'] = '-1' # Market price
            if sl_price:
                algo_order['slTriggerPx'] = str(sl_price)
                algo_order['slOrdPx'] = '-1' # Market price
                
            order_params['attachAlgoOrds'] = [algo_order]
            logger.info(f"Attaching SL/TP: SL={sl_price}, TP={tp_price}")

        try:
            # Set leverage before placing order
            self.data_processor.set_leverage(self.symbol, leverage)
            
            order = None
            if action == 'buy':
                logger.info(f"Executing BUY order for {self.symbol}, contracts: {num_contracts}")
                order = self.data_processor.create_order(self.symbol, 'buy', num_contracts, type='market', params=order_params)
                
            elif action == 'sell':
                # In Perpetual Swap, 'sell' usually means Open Short if no position, or Close Long.
                logger.info(f"Executing SELL order for {self.symbol}, contracts: {num_contracts}")
                order = self.data_processor.create_order(self.symbol, 'sell', num_contracts, type='market', params=order_params)
                
            elif action == 'buy_limit':
                limit_price = decision.get('entry_conditions', {}).get('limit_price')
                if limit_price:
                    logger.info(f"Executing BUY LIMIT order for {self.symbol}, contracts: {num_contracts}, price: {limit_price}")
                    order = self.data_processor.create_order(self.symbol, 'buy', num_contracts, type='limit', price=limit_price, params=order_params)
                else:
                    logger.warning("Buy limit order requested but no limit price provided")
                    
            elif action == 'sell_limit':
                limit_price = decision.get('entry_conditions', {}).get('limit_price')
                if limit_price:
                    logger.info(f"Executing SELL LIMIT order for {self.symbol}, contracts: {num_contracts}, price: {limit_price}")
                    order = self.data_processor.create_order(self.symbol, 'sell', num_contracts, type='limit', price=limit_price, params=order_params)
                else:
                    logger.warning("Sell limit order requested but no limit price provided")
                
            elif action == 'close_buy':
                logger.info(f"Executing CLOSE BUY position for {self.symbol}")
                # Logic to close buy position would go here (e.g., sell current holding)
                # For closing, we might need to know the exact position size to close.
                # Assuming full close for now or handle via specific close logic
                pass
                
            elif action == 'close_sell':
                logger.info(f"Executing CLOSE SELL position for {self.symbol}")
                pass
            
            # Log trade to database if order was created
            if order:
                trade_record = {
                    'symbol': self.symbol,
                    'action': action,
                    'order_type': 'limit' if 'limit' in action else 'market',
                    'contracts': num_contracts,
                    'price': current_price if 'limit' not in action else limit_price,
                    'leverage': leverage,
                    'order_id': order.get('id'),
                    'strategy_rationale': rationale
                }
                self.db_manager.log_trade(trade_record)
                
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")

    def run_once(self):
        """Run a single trading cycle"""
        try:
            logger.info("Starting trading cycle...")
            df, analysis = self.analyze_market()
            
            if df is not None and analysis is not None:
                decision = self.make_decision(df, analysis)
                self.execute_trade(decision)
            
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)

    def start(self):
        """Start the bot loop"""
        self.is_running = True
        logger.info(f"Starting bot for {self.symbol} with {self.interval}s interval")
        
        while self.is_running:
            self.run_once()
            logger.info(f"Waiting {self.interval} seconds before next analysis...")
            time.sleep(self.interval)

if __name__ == "__main__":
    # Example usage
    bot = CryptoTradingBot(symbol='ETH/USDT:USDT', timeframe='15m', interval=900) # 15 minutes interval
    bot.start()
