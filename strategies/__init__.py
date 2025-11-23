"""Trading strategies module"""
from .base_strategy import BaseStrategy
from .ema_options import EMAOptionsStrategy

__all__ = ['BaseStrategy', 'EMAOptionsStrategy']
