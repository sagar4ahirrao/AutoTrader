"""
Base Strategy Class
Abstract base class for all trading strategies
"""
from abc import ABC, abstractmethod
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies
    """
    
    def __init__(self, name, fyers_client, market_data, config_params=None):
        """
        Initialize base strategy
        
        Args:
            name: Strategy name
            fyers_client: FyersClient instance
            market_data: MarketData instance
            config_params: Dictionary of configuration parameters
        """
        self.name = name
        self.fyers_client = fyers_client
        self.market_data = market_data
        self.config = config_params or {}
        
        self.is_running = False
        self.positions = []
        self.signals = []
        self.trade_log = []
        
        logger.info(f"Strategy '{name}' initialized")
    
    @abstractmethod
    def generate_signal(self):
        """
        Generate trading signal
        
        Returns:
            dict: Signal with 'action' (BUY/SELL/HOLD), 'symbol', 'quantity', etc.
        """
        pass
    
    @abstractmethod
    def execute_signal(self, signal):
        """
        Execute a trading signal
        
        Args:
            signal: Signal dictionary from generate_signal()
            
        Returns:
            dict: Execution result
        """
        pass
    
    def start(self):
        """
        Start the strategy
        """
        self.is_running = True
        logger.info(f"Strategy '{self.name}' started")
    
    def stop(self):
        """
        Stop the strategy
        """
        self.is_running = False
        logger.info(f"Strategy '{self.name}' stopped")
    
    def get_status(self):
        """
        Get strategy status
        
        Returns:
            dict: Strategy status information
        """
        return {
            'name': self.name,
            'is_running': self.is_running,
            'positions': len(self.positions),
            'total_trades': len(self.trade_log),
            'config': self.config
        }
    
    def log_trade(self, trade_info):
        """
        Log a trade execution
        
        Args:
            trade_info: Dictionary with trade details
        """
        trade_info['timestamp'] = datetime.now()
        self.trade_log.append(trade_info)
        logger.info(f"Trade logged: {trade_info}")
    
    def add_signal(self, signal):
        """
        Add a signal to history
        
        Args:
            signal: Signal dictionary
        """
        signal['timestamp'] = datetime.now()
        self.signals.append(signal)
        logger.info(f"Signal added: {signal}")
    
    def calculate_position_size(self, capital, price, risk_per_trade=0.02):
        """
        Calculate position size based on available capital and risk
        
        Args:
            capital: Available capital
            price: Entry price
            risk_per_trade: Risk percentage per trade (default: 2%)
            
        Returns:
            int: Position size
        """
        risk_amount = capital * risk_per_trade
        position_size = int(risk_amount / price)
        
        return max(1, position_size)
    
    def calculate_stop_loss(self, entry_price, side, stop_loss_pct=2.0):
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: 1 for BUY, -1 for SELL
            stop_loss_pct: Stop loss percentage
            
        Returns:
            float: Stop loss price
        """
        if side == 1:  # Long position
            return entry_price * (1 - stop_loss_pct / 100)
        else:  # Short position
            return entry_price * (1 + stop_loss_pct / 100)
    
    def calculate_target(self, entry_price, side, target_pct=4.0):
        """
        Calculate target price
        
        Args:
            entry_price: Entry price
            side: 1 for BUY, -1 for SELL
            target_pct: Target percentage
            
        Returns:
            float: Target price
        """
        if side == 1:  # Long position
            return entry_price * (1 + target_pct / 100)
        else:  # Short position
            return entry_price * (1 - target_pct / 100)
    
    def update_positions(self):
        """
        Update positions from broker
        """
        try:
            positions_response = self.fyers_client.get_positions()
            
            if positions_response and positions_response.get('s') == 'ok':
                self.positions = positions_response.get('netPositions', [])
                logger.info(f"Positions updated: {len(self.positions)} active")
            else:
                logger.error(f"Failed to update positions: {positions_response}")
                
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def close_all_positions(self):
        """
        Close all open positions
        
        Returns:
            list: List of close order responses
        """
        results = []
        
        try:
            self.update_positions()
            
            for position in self.positions:
                # Extract position details
                symbol = position.get('symbol')
                quantity = abs(int(position.get('netQty', 0)))
                side = -1 if int(position.get('netQty', 0)) > 0 else 1  # Opposite side to close
                
                if quantity > 0:
                    # Place market order to close
                    result = self.fyers_client.place_order(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type='MARKET'
                    )
                    
                    results.append(result)
                    
                    self.log_trade({
                        'action': 'CLOSE',
                        'symbol': symbol,
                        'quantity': quantity,
                        'result': result
                    })
            
            logger.info(f"Closed {len(results)} positions")
            return results
            
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
            return []
    
    def get_trade_history(self, limit=None):
        """
        Get trade history
        
        Args:
            limit: Maximum number of trades to return (None for all)
            
        Returns:
            list: Trade history
        """
        if limit:
            return self.trade_log[-limit:]
        return self.trade_log
    
    def get_signal_history(self, limit=None):
        """
        Get signal history
        
        Args:
            limit: Maximum number of signals to return (None for all)
            
        Returns:
            list: Signal history
        """
        if limit:
            return self.signals[-limit:]
        return self.signals
    
    def reset(self):
        """
        Reset strategy state
        """
        self.is_running = False
        self.positions = []
        self.signals = []
        self.trade_log = []
        logger.info(f"Strategy '{self.name}' reset")
