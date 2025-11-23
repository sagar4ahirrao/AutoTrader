"""
Market Data Module
Fetches real-time and historical market data from Fyers API
"""
import logging
import pandas as pd
from datetime import datetime, timedelta
import config
from utils.helpers import get_date_range

logger = logging.getLogger(__name__)


class MarketData:
    """
    Market Data Handler for Fyers API
    """
    
    def __init__(self, fyers_model=None):
        """
        Initialize Market Data handler
        
        Args:
            fyers_model: Initialized fyersModel.FyersModel instance
        """
        self.fyers = fyers_model
        logger.info("MarketData initialized")
    
    def set_fyers_model(self, fyers_model):
        """
        Set the Fyers model instance
        
        Args:
            fyers_model: Initialized fyersModel.FyersModel instance
        """
        self.fyers = fyers_model
    
    def get_historical_data(self, symbol, days=30, timeframe='5'):
        """
        Get historical candle data
        
        Args:
            symbol: Trading symbol (e.g., "NSE:SBIN-EQ")
            days: Number of days of historical data
            timeframe: Candle timeframe ('1', '5', '15', '30', '60', 'D')
            
        Returns:
            pandas DataFrame with historical data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            from_date, to_date = get_date_range(days)
            
            data = {
                "symbol": symbol,
                "resolution": timeframe,
                "date_format": "1",
                "range_from": str(from_date),
                "range_to": str(to_date),
                "cont_flag": "1"
            }
            
            response = self.fyers.history(data)
            
            if response.get('s') == 'ok' and 'candles' in response:
                # Convert to DataFrame
                df = pd.DataFrame(
                    response['candles'],
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                # Convert timestamp to datetime
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('datetime', inplace=True)
                
                logger.info(f"Historical data fetched for {symbol}: {len(df)} candles")
                return df
            else:
                logger.error(f"Failed to fetch historical data: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def get_quotes(self, symbols):
        """
        Get real-time quotes for symbols
        
        Args:
            symbols: List of symbols or single symbol string
            
        Returns:
            dict: Quote data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
            
            data = {
                "symbols": ",".join(symbols)
            }
            
            response = self.fyers.quotes(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Quotes fetched for {len(symbols)} symbols")
            else:
                logger.error(f"Failed to fetch quotes: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return None
    
    def get_depth(self, symbol):
        """
        Get market depth (order book) for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: Market depth data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            data = {
                "symbol": symbol,
                "ohlcv_flag": "1"
            }
            
            response = self.fyers.depth(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Market depth fetched for {symbol}")
            else:
                logger.error(f"Failed to fetch market depth: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching market depth: {e}")
            return None
    
    def get_option_chain(self, symbol, expiry=None):
        """
        Get options chain data
        
        Args:
            symbol: Underlying symbol (e.g., "NSE:NIFTY50-INDEX")
            expiry: Expiry date (optional, format: "YYMMM" e.g., "24DEC")
            
        Returns:
            dict: Option chain data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            # Get symbol info first to find strikes
            data = {
                "symbol": symbol
            }
            
            # Note: Fyers API v3 doesn't have direct option chain endpoint
            # We need to construct option symbols and fetch quotes
            # This is a simplified implementation
            
            logger.warning("Option chain fetching requires manual symbol construction")
            return {"s": "error", "message": "Option chain not directly supported"}
            
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}")
            return None
    
    def search_symbols(self, query):
        """
        Search for symbols
        
        Args:
            query: Search query string
            
        Returns:
            dict: Search results
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            data = {
                "symbol": query,
                "n": 10  # Number of results
            }
            
            response = self.fyers.search_syms(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Symbol search completed for: {query}")
            else:
                logger.error(f"Symbol search failed: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return None
    
    def get_current_price(self, symbol):
        """
        Get current market price for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            float: Current price, or None if error
        """
        quotes = self.get_quotes(symbol)
        
        if quotes and quotes.get('s') == 'ok' and 'd' in quotes:
            symbol_data = quotes['d'][0]
            if 'v' in symbol_data and 'lp' in symbol_data['v']:
                return float(symbol_data['v']['lp'])
        
        return None
    
    def calculate_ltp_change(self, symbol):
        """
        Calculate LTP change percentage
        
        Args:
            symbol: Trading symbol
            
        Returns:
            dict: {'ltp': float, 'change': float, 'change_pct': float}
        """
        quotes = self.get_quotes(symbol)
        
        if quotes and quotes.get('s') == 'ok' and 'd' in quotes:
            symbol_data = quotes['d'][0]['v']
            
            ltp = float(symbol_data.get('lp', 0))
            prev_close = float(symbol_data.get('prev_close_price', ltp))
            
            change = ltp - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0
            
            return {
                'ltp': ltp,
                'change': change,
                'change_pct': change_pct
            }
        
        return None
