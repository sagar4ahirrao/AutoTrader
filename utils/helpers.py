"""
Helper Utility Functions
"""
import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def format_symbol(symbol):
    """
    Format a symbol string for Fyers API
    
    Args:
        symbol: Symbol string (e.g., "NIFTY", "BANKNIFTY", "SBIN")
        
    Returns:
        Formatted symbol string (e.g., "NSE:SBIN-EQ")
    """
    symbol = symbol.upper().strip()
    
    # If already formatted, return as is
    if ':' in symbol:
        return symbol
    
    # Common index symbols
    index_map = {
        'NIFTY': 'NSE:NIFTY50-INDEX',
        'NIFTY50': 'NSE:NIFTY50-INDEX',
        'BANKNIFTY': 'NSE:NIFTYBANK-INDEX',
        'NIFTYBANK': 'NSE:NIFTYBANK-INDEX',
        'FINNIFTY': 'NSE:FINNIFTY-INDEX',
    }
    
    if symbol in index_map:
        return index_map[symbol]
    
    # Default to NSE equity
    return f"NSE:{symbol}-EQ"


def validate_symbol(symbol):
    """
    Validate if a symbol string is properly formatted
    
    Args:
        symbol: Symbol string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not symbol:
        return False
    
    # Fyers symbol format: EXCHANGE:SYMBOL-SEGMENT
    pattern = r'^[A-Z]+:[A-Z0-9]+-[A-Z]+$'
    return bool(re.match(pattern, symbol))


def get_timestamp(days_ago=0):
    """
    Get timestamp for a given number of days ago
    
    Args:
        days_ago: Number of days in the past (0 = today)
        
    Returns:
        Unix timestamp (seconds)
    """
    target_date = datetime.now() - timedelta(days=days_ago)
    return int(target_date.timestamp())


def get_date_range(days=30):
    """
    Get date range for historical data
    
    Args:
        days: Number of days of historical data
        
    Returns:
        tuple: (from_timestamp, to_timestamp)
    """
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    return int(from_date.timestamp()), int(to_date.timestamp())


def parse_option_symbol(symbol):
    """
    Parse an option symbol to extract components
    
    Args:
        symbol: Option symbol (e.g., "NSE:NIFTY24DEC24000CE")
        
    Returns:
        dict with 'exchange', 'underlying', 'expiry', 'strike', 'option_type'
    """
    try:
        # Split exchange and rest
        parts = symbol.split(':')
        if len(parts) != 2:
            return None
        
        exchange = parts[0]
        option_part = parts[1]
        
        # Pattern for option symbol: UNDERLYING + EXPIRY + STRIKE + CE/PE
        # Example: NIFTY24DEC24000CE
        pattern = r'([A-Z]+)(\d{2}[A-Z]{3})(\d+)(CE|PE)'
        match = re.match(pattern, option_part)
        
        if not match:
            return None
        
        return {
            'exchange': exchange,
            'underlying': match.group(1),
            'expiry': match.group(2),
            'strike': int(match.group(3)),
            'option_type': match.group(4)
        }
    except Exception as e:
        logger.error(f"Error parsing option symbol {symbol}: {e}")
        return None


def format_price(price):
    """
    Format price for display
    
    Args:
        price: Price value
        
    Returns:
        Formatted price string
    """
    if price is None:
        return "N/A"
    
    try:
        return f"₹{float(price):,.2f}"
    except (ValueError, TypeError):
        return str(price)


def format_pnl(pnl):
    """
    Format P&L with color indication
    
    Args:
        pnl: Profit/Loss value
        
    Returns:
        Formatted P&L string
    """
    if pnl is None:
        return "N/A"
    
    try:
        pnl_float = float(pnl)
        sign = "+" if pnl_float >= 0 else ""
        return f"{sign}₹{pnl_float:,.2f}"
    except (ValueError, TypeError):
        return str(pnl)


def calculate_quantity_from_capital(capital, price, lot_size=1):
    """
    Calculate quantity based on available capital
    
    Args:
        capital: Available capital
        price: Price per unit
        lot_size: Minimum lot size
        
    Returns:
        Quantity to trade (in lots)
    """
    if price <= 0:
        return 0
    
    max_quantity = int(capital / price)
    lots = max_quantity // lot_size
    
    return lots * lot_size


def is_market_open():
    """
    Check if market is currently open (simple version)
    
    Returns:
        bool: True if market should be open
    """
    now = datetime.now()
    
    # Market closed on weekends
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Market hours: 9:15 AM to 3:30 PM IST
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_open <= now <= market_close


def get_next_expiry_date():
    """
    Get next weekly option expiry date (Thursday)
    
    Returns:
        datetime object for next expiry
    """
    today = datetime.now()
    days_ahead = 3 - today.weekday()  # Thursday = 3
    
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    next_expiry = today + timedelta(days=days_ahead)
    return next_expiry


def truncate_string(text, max_length=50):
    """
    Truncate string with ellipsis if too long
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string
    """
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."
