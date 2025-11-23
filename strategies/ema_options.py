"""
EMA-based Options Trading Strategy
Demonstration strategy using EMA crossover for options trading
"""
import logging
from strategies.base_strategy import BaseStrategy
from utils.indicators import calculate_ema, detect_crossover
from utils.helpers import format_symbol
import config

logger = logging.getLogger(__name__)


class EMAOptionsStrategy(BaseStrategy):
    """
    EMA Crossover Strategy for Options Trading
    
    Strategy Logic:
    - Calculate Fast EMA and Slow EMA on underlying index
    - Buy Call option when Fast EMA crosses above Slow EMA (bullish)
    - Buy Put option when Fast EMA crosses below Slow EMA (bearish)
    - Exit on opposite crossover or target/stop-loss hit
    """
    
    def __init__(self, fyers_client, market_data, config_params=None):
        """
        Initialize EMA Options Strategy
        
        Args:
            fyers_client: FyersClient instance
            market_data: MarketData instance
            config_params: Strategy configuration parameters
        """
        super().__init__("EMA Options Strategy", fyers_client, market_data, config_params)
        
        # Strategy parameters
        self.underlying_symbol = self.config.get('underlying_symbol', config.NIFTY_SYMBOL)
        self.fast_ema_period = self.config.get('fast_ema_period', config.DEFAULT_FAST_EMA)
        self.slow_ema_period = self.config.get('slow_ema_period', config.DEFAULT_SLOW_EMA)
        self.timeframe = self.config.get('timeframe', '5')
        self.position_size = self.config.get('position_size', config.DEFAULT_POSITION_SIZE)
        self.stop_loss_pct = self.config.get('stop_loss_pct', config.DEFAULT_STOP_LOSS_PCT)
        self.target_pct = self.config.get('target_pct', config.DEFAULT_TARGET_PCT)
        
        # State variables
        self.current_position = None
        self.last_signal = None
        
        logger.info(f"EMA Strategy initialized with Fast: {self.fast_ema_period}, Slow: {self.slow_ema_period}")
    
    def generate_signal(self):
        """
        Generate trading signal based on EMA crossover
        
        Returns:
            dict: Signal with action, symbol, quantity, etc.
        """
        try:
            # Fetch historical data for underlying
            df = self.market_data.get_historical_data(
                symbol=self.underlying_symbol,
                days=10,  # Enough data for EMA calculation
                timeframe=self.timeframe
            )
            
            if df is None or len(df) < self.slow_ema_period + 5:
                logger.warning("Insufficient data for EMA calculation")
                return {'action': 'HOLD', 'reason': 'Insufficient data'}
            
            # Calculate EMAs
            fast_ema = calculate_ema(df, self.fast_ema_period)
            slow_ema = calculate_ema(df, self.slow_ema_period)
            
            # Detect crossover
            signal_type, crossover = detect_crossover(fast_ema, slow_ema)
            
            # Get current price
            current_price = df['close'].iloc[-1]
            
            # Generate signal
            signal = {
                'timestamp': df.index[-1],
                'underlying': self.underlying_symbol,
                'current_price': current_price,
                'fast_ema': fast_ema.iloc[-1],
                'slow_ema': slow_ema.iloc[-1],
                'signal_type': signal_type,
                'crossover': crossover
            }
            
            # Determine action
            if crossover == 'bullish_cross':
                # Bullish crossover - Buy Call option
                signal['action'] = 'BUY_CALL'
                signal['option_type'] = 'CE'
                signal['reason'] = 'Bullish EMA crossover'
                
            elif crossover == 'bearish_cross':
                # Bearish crossover - Buy Put option
                signal['action'] = 'BUY_PUT'
                signal['option_type'] = 'PE'
                signal['reason'] = 'Bearish EMA crossover'
                
            else:
                # No crossover - check if we should exit existing position
                if self.current_position:
                    if self._should_exit_position(signal_type):
                        signal['action'] = 'EXIT'
                        signal['reason'] = 'Exit signal from opposite trend'
                    else:
                        signal['action'] = 'HOLD'
                        signal['reason'] = 'Continue holding position'
                else:
                    signal['action'] = 'HOLD'
                    signal['reason'] = 'No crossover detected'
            
            # Add signal to history
            self.add_signal(signal)
            self.last_signal = signal
            
            logger.info(f"Signal generated: {signal['action']} - {signal.get('reason')}")
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return {'action': 'HOLD', 'reason': f'Error: {str(e)}'}
    
    def execute_signal(self, signal):
        """
        Execute a trading signal
        
        Args:
            signal: Signal dictionary from generate_signal()
            
        Returns:
            dict: Execution result
        """
        action = signal.get('action')
        
        try:
            if action == 'HOLD':
                return {'status': 'success', 'message': 'Holding position'}
            
            elif action in ['BUY_CALL', 'BUY_PUT']:
                return self._execute_entry(signal)
            
            elif action == 'EXIT':
                return self._execute_exit(signal)
            
            else:
                logger.warning(f"Unknown action: {action}")
                return {'status': 'error', 'message': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _execute_entry(self, signal):
        """
        Execute entry order for option
        
        Args:
            signal: Signal dictionary
            
        Returns:
            dict: Execution result
        """
        # Close existing position if any
        if self.current_position:
            logger.info("Closing existing position before new entry")
            self._execute_exit(signal)
        
        # For demonstration, we'll use a simplified approach
        # In production, you'd need to:
        # 1. Find the appropriate strike price (ATM/OTM)
        # 2. Get the correct options symbol
        # 3. Fetch the option premium
        
        option_type = signal.get('option_type', 'CE')
        
        # Simplified: Use underlying symbol as placeholder
        # In reality, construct proper option symbol:
        # Example: "NSE:NIFTY24DEC24000CE" for NIFTY call at 24000 strike
        
        logger.warning("Option symbol construction needed - using simplified demo mode")
        
        # Create a demo position entry
        entry_info = {
            'symbol': f"{self.underlying_symbol}-{option_type}",
            'option_type': option_type,
            'entry_price': signal.get('current_price', 0),
            'quantity': self.position_size,
            'entry_time': signal.get('timestamp'),
            'stop_loss': self.calculate_stop_loss(signal.get('current_price', 0), 1, self.stop_loss_pct),
            'target': self.calculate_target(signal.get('current_price', 0), 1, self.target_pct),
            'signal': signal
        }
        
        # In paper trading or demo mode
        if config.TRADING_MODE == 'PAPER':
            logger.info(f"PAPER TRADE - Entry: {entry_info}")
            self.current_position = entry_info
            self.log_trade({
                'type': 'ENTRY',
                'mode': 'PAPER',
                **entry_info
            })
            return {'status': 'success', 'message': 'Paper trade executed', 'position': entry_info}
        
        # For live trading, place actual order
        else:
            # Note: This would need proper option symbol
            logger.error("Live trading requires proper option symbol - not implemented in demo")
            return {'status': 'error', 'message': 'Option symbol construction required for live trading'}
    
    def _execute_exit(self, signal):
        """
        Execute exit order for current position
        
        Args:
            signal: Signal dictionary
            
        Returns:
            dict: Execution result
        """
        if not self.current_position:
            return {'status': 'success', 'message': 'No position to exit'}
        
        # Calculate P&L
        entry_price = self.current_position.get('entry_price', 0)
        current_price = signal.get('current_price', entry_price)
        quantity = self.current_position.get('quantity', 0)
        
        pnl = (current_price - entry_price) * quantity
        pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price != 0 else 0
        
        exit_info = {
            'symbol': self.current_position['symbol'],
            'exit_price': current_price,
            'exit_time': signal.get('timestamp'),
            'entry_price': entry_price,
            'quantity': quantity,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': signal.get('reason', 'Exit signal')
        }
        
        # In paper trading mode
        if config.TRADING_MODE == 'PAPER':
            logger.info(f"PAPER TRADE - Exit: {exit_info}")
            self.log_trade({
                'type': 'EXIT',
                'mode': 'PAPER',
                **exit_info
            })
            self.current_position = None
            return {'status': 'success', 'message': 'Paper trade exit executed', 'exit': exit_info}
        
        # For live trading
        else:
            logger.error("Live trading exit requires actual order placement")
            return {'status': 'error', 'message': 'Live trading not implemented in demo'}
    
    def _should_exit_position(self, current_signal_type):
        """
        Determine if current position should be exited
        
        Args:
            current_signal_type: Current signal type (1 for bullish, -1 for bearish)
            
        Returns:
            bool: True if should exit
        """
        if not self.current_position:
            return False
        
        option_type = self.current_position.get('option_type')
        
        # Exit Call position if signal turns bearish
        if option_type == 'CE' and current_signal_type == -1:
            return True
        
        # Exit Put position if signal turns bullish
        if option_type == 'PE' and current_signal_type == 1:
            return True
        
        return False
    
    def run_iteration(self):
        """
        Run one iteration of the strategy
        
        Returns:
            dict: Iteration result with signal and execution
        """
        if not self.is_running:
            return {'status': 'stopped', 'message': 'Strategy not running'}
        
        try:
            # Generate signal
            signal = self.generate_signal()
            
            # Execute signal
            execution = self.execute_signal(signal)
            
            return {
                'status': 'success',
                'signal': signal,
                'execution': execution
            }
            
        except Exception as e:
            logger.error(f"Error in strategy iteration: {e}")
            return {'status': 'error', 'message': str(e)}
