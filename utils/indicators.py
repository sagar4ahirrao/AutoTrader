"""
Technical Indicators Module
Calculate various technical indicators for trading strategies
"""
import pandas as pd
import numpy as np


def calculate_ema(data, period):
    """
    Calculate Exponential Moving Average
    
    Args:
        data: pandas Series or DataFrame with price data
        period: EMA period
        
    Returns:
        pandas Series with EMA values
    """
    if isinstance(data, pd.DataFrame):
        # If DataFrame, use 'close' column
        if 'close' in data.columns:
            prices = data['close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            prices = data.iloc[:, -1]  # Use last column
    else:
        prices = data
    
    return prices.ewm(span=period, adjust=False).mean()


def calculate_sma(data, period):
    """
    Calculate Simple Moving Average
    
    Args:
        data: pandas Series or DataFrame with price data
        period: SMA period
        
    Returns:
        pandas Series with SMA values
    """
    if isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            prices = data['close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            prices = data.iloc[:, -1]
    else:
        prices = data
    
    return prices.rolling(window=period).mean()


def detect_crossover(fast_series, slow_series):
    """
    Detect crossover between two series (e.g., fast EMA and slow EMA)
    
    Args:
        fast_series: pandas Series with fast indicator values
        slow_series: pandas Series with slow indicator values
        
    Returns:
        tuple: (current_signal, crossover_type)
            current_signal: 1 (bullish), -1 (bearish), 0 (neutral)
            crossover_type: 'bullish_cross', 'bearish_cross', or None
    """
    # Get the last two values
    if len(fast_series) < 2 or len(slow_series) < 2:
        return 0, None
    
    fast_current = fast_series.iloc[-1]
    fast_prev = fast_series.iloc[-2]
    slow_current = slow_series.iloc[-1]
    slow_prev = slow_series.iloc[-2]
    
    # Detect bullish crossover (fast crosses above slow)
    if fast_prev <= slow_prev and fast_current > slow_current:
        return 1, 'bullish_cross'
    
    # Detect bearish crossover (fast crosses below slow)
    elif fast_prev >= slow_prev and fast_current < slow_current:
        return -1, 'bearish_cross'
    
    # No crossover, return current position
    elif fast_current > slow_current:
        return 1, None
    elif fast_current < slow_current:
        return -1, None
    else:
        return 0, None


def calculate_rsi(data, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        data: pandas Series or DataFrame with price data
        period: RSI period (default: 14)
        
    Returns:
        pandas Series with RSI values
    """
    if isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            prices = data['close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            prices = data.iloc[:, -1]
    else:
        prices = data
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        data: pandas Series or DataFrame with price data
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)
        
    Returns:
        tuple: (macd_line, signal_line, histogram)
    """
    if isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            prices = data['close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            prices = data.iloc[:, -1]
    else:
        prices = data
    
    # Calculate MACD line
    fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
    slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    
    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    
    Args:
        data: pandas Series or DataFrame with price data
        period: Moving average period (default: 20)
        std_dev: Number of standard deviations (default: 2)
        
    Returns:
        tuple: (upper_band, middle_band, lower_band)
    """
    if isinstance(data, pd.DataFrame):
        if 'close' in data.columns:
            prices = data['close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            prices = data.iloc[:, -1]
    else:
        prices = data
    
    # Calculate middle band (SMA)
    middle_band = prices.rolling(window=period).mean()
    
    # Calculate standard deviation
    std = prices.rolling(window=period).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band
