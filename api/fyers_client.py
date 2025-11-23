"""
Fyers API Client
Wrapper for Fyers trading operations
"""
import logging
from fyers_apiv3 import fyersModel
import config

logger = logging.getLogger(__name__)


class FyersClient:
    """
    Fyers API Client for trading operations
    """
    
    def __init__(self, fyers_model=None):
        """
        Initialize Fyers Client
        
        Args:
            fyers_model: Initialized fyersModel.FyersModel instance
        """
        self.fyers = fyers_model
        logger.info("FyersClient initialized")
    
    def set_fyers_model(self, fyers_model):
        """
        Set the Fyers model instance
        
        Args:
            fyers_model: Initialized fyersModel.FyersModel instance
        """
        self.fyers = fyers_model
    
    def place_order(self, symbol, side, quantity, order_type='MARKET', price=0, 
                    stop_loss=0, take_profit=0, product_type='INTRADAY'):
        """
        Place an order
        
        Args:
            symbol: Trading symbol (e.g., "NSE:SBIN-EQ")
            side: 1 for BUY, -1 for SELL
            quantity: Order quantity
            order_type: Order type - MARKET, LIMIT, STOP, etc.
            price: Limit price (for LIMIT orders)
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            product_type: Product type - INTRADAY, MARGIN, CNC
            
        Returns:
            dict: Order response
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            data = {
                "symbol": symbol,
                "qty": quantity,
                "type": config.ORDER_TYPE_MARKET if order_type == 'MARKET' else config.ORDER_TYPE_LIMIT,
                "side": side,
                "productType": product_type,
                "limitPrice": price if order_type != 'MARKET' else 0,
                "stopPrice": 0,
                "validity": config.VALIDITY_DAY,
                "disclosedQty": 0,
                "offlineOrder": False,
                "stopLoss": stop_loss,
                "takeProfit": take_profit
            }
            
            response = self.fyers.place_order(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Order placed successfully: {response}")
            else:
                logger.error(f"Order placement failed: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"s": "error", "message": str(e)}
    
    def modify_order(self, order_id, quantity=None, price=None, order_type=None):
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity (optional)
            price: New price (optional)
            order_type: New order type (optional)
            
        Returns:
            dict: Modification response
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            data = {
                "id": order_id
            }
            
            if quantity:
                data["qty"] = quantity
            if price:
                data["limitPrice"] = price
            if order_type:
                data["type"] = config.ORDER_TYPE_MARKET if order_type == 'MARKET' else config.ORDER_TYPE_LIMIT
            
            response = self.fyers.modify_order(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Order modified successfully: {response}")
            else:
                logger.error(f"Order modification failed: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return {"s": "error", "message": str(e)}
    
    def cancel_order(self, order_id):
        """
        Cancel an existing order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            dict: Cancellation response
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            data = {
                "id": order_id
            }
            
            response = self.fyers.cancel_order(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Order cancelled successfully: {response}")
            else:
                logger.error(f"Order cancellation failed: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return {"s": "error", "message": str(e)}
    
    def get_orders(self):
        """
        Get all orders
        
        Returns:
            dict: Orders data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            response = self.fyers.orderbook()
            logger.info("Orders fetched successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return {"s": "error", "message": str(e)}
    
    def get_positions(self):
        """
        Get all positions
        
        Returns:
            dict: Positions data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            response = self.fyers.positions()
            logger.info("Positions fetched successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {"s": "error", "message": str(e)}
    
    def get_holdings(self):
        """
        Get all holdings
        
        Returns:
            dict: Holdings data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            response = self.fyers.holdings()
            logger.info("Holdings fetched successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching holdings: {e}")
            return {"s": "error", "message": str(e)}
    
    def get_tradebook(self):
        """
        Get trade history
        
        Returns:
            dict: Tradebook data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            response = self.fyers.tradebook()
            logger.info("Tradebook fetched successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching tradebook: {e}")
            return {"s": "error", "message": str(e)}
    
    def exit_position(self, position_id):
        """
        Exit a specific position
        
        Args:
            position_id: Position ID to exit
            
        Returns:
            dict: Exit response
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            data = {
                "id": position_id
            }
            
            response = self.fyers.exit_positions(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Position exited successfully: {response}")
            else:
                logger.error(f"Position exit failed: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error exiting position: {e}")
            return {"s": "error", "message": str(e)}
    
    def convert_position(self, symbol, quantity, from_product, to_product, side):
        """
        Convert position from one product type to another
        
        Args:
            symbol: Trading symbol
            quantity: Quantity to convert
            from_product: Current product type
            to_product: Target product type
            side: Position side (1 for long, -1 for short)
            
        Returns:
            dict: Conversion response
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return {"s": "error", "message": "Client not initialized"}
        
        try:
            data = {
                "symbol": symbol,
                "positionSide": side,
                "convertQty": quantity,
                "convertFrom": from_product,
                "convertTo": to_product
            }
            
            response = self.fyers.convert_position(data)
            
            if response.get('s') == 'ok':
                logger.info(f"Position converted successfully: {response}")
            else:
                logger.error(f"Position conversion failed: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error converting position: {e}")
            return {"s": "error", "message": str(e)}
