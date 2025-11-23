"""
Configuration management for Fyers Algo Trading Application
"""
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Fyers API Configuration
FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID', '')
FYERS_SECRET_KEY = os.getenv('FYERS_SECRET_KEY', '')
FYERS_REDIRECT_URL = os.getenv('FYERS_REDIRECT_URL', 'http://localhost:8501')

# Webhook Configuration
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 5000))
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN', '')

# Strategy Default Parameters
DEFAULT_FAST_EMA = int(os.getenv('DEFAULT_FAST_EMA', 9))
DEFAULT_SLOW_EMA = int(os.getenv('DEFAULT_SLOW_EMA', 21))
DEFAULT_POSITION_SIZE = int(os.getenv('DEFAULT_POSITION_SIZE', 1))

# Risk Management
DEFAULT_STOP_LOSS_PCT = float(os.getenv('DEFAULT_STOP_LOSS_PCT', 2.0))
DEFAULT_TARGET_PCT = float(os.getenv('DEFAULT_TARGET_PCT', 4.0))

# Trading Mode
TRADING_MODE = os.getenv('TRADING_MODE', 'PAPER')

# Fyers API Constants
FYERS_BASE_URL = "https://api-t1.fyers.in/api/v3"
FYERS_AUTH_URL = "https://api-t2.fyers.in/vagator/v2"

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('trading_app.log')
        ]
    )
    return logging.getLogger(__name__)

# Market Data Configuration
CANDLE_TIMEFRAMES = {
    '1min': '1',
    '5min': '5',
    '15min': '15',
    '30min': '30',
    '1hour': '60',
    '1day': 'D'
}

# Common Symbols
NIFTY_SYMBOL = "NSE:NIFTY50-INDEX"
BANKNIFTY_SYMBOL = "NSE:NIFTYBANK-INDEX"

# Order Types
ORDER_TYPE_LIMIT = 1
ORDER_TYPE_MARKET = 2
ORDER_TYPE_STOP = 3
ORDER_TYPE_STOPLIMIT = 4

# Order Side
SIDE_BUY = 1
SIDE_SELL = -1

# Product Types
PRODUCT_INTRADAY = "INTRADAY"
PRODUCT_MARGIN = "MARGIN"
PRODUCT_CNC = "CNC"

# Validity
VALIDITY_DAY = "DAY"
VALIDITY_IOC = "IOC"
