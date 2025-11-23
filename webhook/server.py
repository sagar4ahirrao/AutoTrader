"""
Webhook Server for TradingView Integration
Flask-based server to receive and process TradingView alerts
"""
import logging
from flask import Flask, request, jsonify
from threading import Thread
import config

logger = logging.getLogger(__name__)


class WebhookServer:
    """
    Webhook server for receiving TradingView alerts
    """
    
    def __init__(self, port=None, token=None):
        """
        Initialize webhook server
        
        Args:
            port: Server port (default from config)
            token: Security token for webhook authentication
        """
        self.port = port or config.WEBHOOK_PORT
        self.token = token or config.WEBHOOK_TOKEN
        
        self.app = Flask(__name__)
        self.server_thread = None
        self.is_running = False
        
        # Callback function to execute trades
        self.trade_callback = None
        
        # Webhook logs
        self.webhook_logs = []
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"WebhookServer initialized on port {self.port}")
    
    def _setup_routes(self):
        """
        Setup Flask routes
        """
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'ok',
                'server': 'Fyers Auto Trading Webhook',
                'version': '1.0'
            })
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Main webhook endpoint for TradingView alerts"""
            try:
                # Get JSON payload
                data = request.get_json()
                
                if not data:
                    logger.warning("No data received in webhook")
                    return jsonify({'status': 'error', 'message': 'No data received'}), 400
                
                # Validate token
                request_token = data.get('token')
                if not request_token or request_token != self.token:
                    logger.warning(f"Invalid token received: {request_token}")
                    return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
                
                # Extract trade parameters
                action = data.get('action', '').upper()
                symbol = data.get('symbol', '')
                quantity = data.get('quantity', 0)
                order_type = data.get('order_type', 'MARKET').upper()
                price = data.get('price', 0)
                
                # Validate required fields
                if not action or not symbol:
                    logger.warning("Missing required fields in webhook")
                    return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
                
                if action not in ['BUY', 'SELL', 'EXIT']:
                    logger.warning(f"Invalid action: {action}")
                    return jsonify({'status': 'error', 'message': 'Invalid action'}), 400
                
                # Log webhook
                webhook_log = {
                    'action': action,
                    'symbol': symbol,
                    'quantity': quantity,
                    'order_type': order_type,
                    'price': price,
                    'data': data
                }
                self._add_log(webhook_log)
                
                logger.info(f"Webhook received: {action} {symbol} x {quantity}")
                
                # Execute trade callback if set
                if self.trade_callback:
                    try:
                        result = self.trade_callback(webhook_log)
                        return jsonify({
                            'status': 'success',
                            'message': 'Trade executed',
                            'result': result
                        })
                    except Exception as e:
                        logger.error(f"Error executing trade callback: {e}")
                        return jsonify({
                            'status': 'error',
                            'message': f'Trade execution failed: {str(e)}'
                        }), 500
                else:
                    logger.warning("No trade callback set")
                    return jsonify({
                        'status': 'success',
                        'message': 'Webhook received but no callback set'
                    })
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/logs', methods=['GET'])
        def logs():
            """Get webhook logs"""
            limit = request.args.get('limit', 50, type=int)
            return jsonify({
                'status': 'ok',
                'logs': self.webhook_logs[-limit:]
            })
    
    def _add_log(self, log_entry):
        """
        Add log entry
        
        Args:
            log_entry: Dictionary with log data
        """
        from datetime import datetime
        log_entry['timestamp'] = datetime.now().isoformat()
        self.webhook_logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(self.webhook_logs) > 1000:
            self.webhook_logs = self.webhook_logs[-1000:]
    
    def set_trade_callback(self, callback):
        """
        Set callback function for trade execution
        
        Args:
            callback: Function to call with webhook data
                     Should accept webhook_log dict and return result
        """
        self.trade_callback = callback
        logger.info("Trade callback set")
    
    def start(self):
        """
        Start the webhook server in a background thread
        """
        if self.is_running:
            logger.warning("Server already running")
            return
        
        def run_server():
            logger.info(f"Starting webhook server on port {self.port}")
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        
        logger.info(f"Webhook server started on http://localhost:{self.port}")
    
    def stop(self):
        """
        Stop the webhook server
        Note: Flask doesn't support graceful shutdown easily in this setup
        """
        self.is_running = False
        logger.info("Webhook server stop requested (may require restart)")
    
    def get_webhook_url(self):
        """
        Get the webhook URL
        
        Returns:
            str: Webhook URL
        """
        return f"http://localhost:{self.port}/webhook"
    
    def get_logs(self, limit=50):
        """
        Get recent webhook logs
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            list: Recent webhook logs
        """
        return self.webhook_logs[-limit:]
    
    def clear_logs(self):
        """
        Clear all webhook logs
        """
        self.webhook_logs = []
        logger.info("Webhook logs cleared")
    
    def test_webhook(self):
        """
        Generate a test webhook request for testing
        
        Returns:
            dict: Test webhook data
        """
        test_data = {
            'token': self.token,
            'action': 'BUY',
            'symbol': 'NSE:SBIN-EQ',
            'quantity': 1,
            'order_type': 'MARKET',
            'price': 0
        }
        
        logger.info("Test webhook data generated")
        return test_data
