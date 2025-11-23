"""
Fyers Authentication Module
Handles OAuth 2.0 authentication flow for Fyers API
"""
import logging
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import order_ws
import webbrowser
from urllib.parse import urlparse, parse_qs
import config

logger = logging.getLogger(__name__)


class FyersAuth:
    """
    Fyers Authentication Handler
    Manages OAuth flow and access token generation
    """
    
    def __init__(self, client_id=None, secret_key=None, redirect_url=None):
        """
        Initialize Fyers Authentication
        
        Args:
            client_id: Fyers App ID (optional, will use config if not provided)
            secret_key: Fyers App Secret (optional, will use config if not provided)
            redirect_url: OAuth redirect URL (optional, will use config if not provided)
        """
        self.client_id = client_id or config.FYERS_CLIENT_ID
        self.secret_key = secret_key or config.FYERS_SECRET_KEY
        self.redirect_url = redirect_url or config.FYERS_REDIRECT_URL
        
        self.access_token = None
        self.fyers = None
        
        logger.info("FyersAuth initialized")
    
    def generate_auth_url(self):
        """
        Generate the authentication URL for user login
        
        Returns:
            str: Authentication URL for user to visit
        """
        try:
            session = fyersModel.SessionModel(
                client_id=self.client_id,
                secret_key=self.secret_key,
                redirect_uri=self.redirect_url,
                response_type='code',
                grant_type='authorization_code'
            )
            
            auth_url = session.generate_authcode()
            logger.info("Authentication URL generated successfully")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating auth URL: {e}")
            raise
    
    def open_auth_url(self):
        """
        Open authentication URL in browser
        
        Returns:
            str: Authentication URL
        """
        auth_url = self.generate_auth_url()
        
        try:
            webbrowser.open(auth_url)
            logger.info("Opened authentication URL in browser")
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
        
        return auth_url
    
    def extract_auth_code(self, redirect_response):
        """
        Extract authorization code from redirect URL
        
        Args:
            redirect_response: Full redirect URL after user authentication
            
        Returns:
            str: Authorization code
        """
        try:
            parsed_url = urlparse(redirect_response)
            params = parse_qs(parsed_url.query)
            
            if 'auth_code' in params:
                auth_code = params['auth_code'][0]
                logger.info("Authorization code extracted successfully")
                return auth_code
            else:
                logger.error("No auth_code found in redirect URL")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting auth code: {e}")
            return None
    
    def generate_access_token(self, auth_code):
        """
        Generate access token from authorization code
        
        Args:
            auth_code: Authorization code from redirect URL
            
        Returns:
            str: Access token
        """
        try:
            session = fyersModel.SessionModel(
                client_id=self.client_id,
                secret_key=self.secret_key,
                redirect_uri=self.redirect_url,
                response_type='code',
                grant_type='authorization_code'
            )
            
            session.set_token(auth_code)
            response = session.generate_token()
            
            if 'access_token' in response:
                self.access_token = response['access_token']
                logger.info("Access token generated successfully")
                
                # Initialize Fyers client with access token
                self.initialize_client()
                
                return self.access_token
            else:
                logger.error(f"Failed to generate access token: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            raise
    
    def initialize_client(self):
        """
        Initialize Fyers client with access token
        
        Returns:
            fyersModel.FyersModel: Initialized Fyers client
        """
        if not self.access_token:
            logger.error("No access token available")
            return None
        
        try:
            self.fyers = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                log_path=""
            )
            
            logger.info("Fyers client initialized successfully")
            return self.fyers
            
        except Exception as e:
            logger.error(f"Error initializing Fyers client: {e}")
            raise
    
    def set_access_token(self, access_token):
        """
        Set access token manually (e.g., from session storage)
        
        Args:
            access_token: Access token string
        """
        self.access_token = access_token
        self.initialize_client()
        logger.info("Access token set manually")
    
    def get_profile(self):
        """
        Get user profile information
        
        Returns:
            dict: User profile data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            response = self.fyers.get_profile()
            logger.info("Profile retrieved successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return None
    
    def get_funds(self):
        """
        Get account funds/balance information
        
        Returns:
            dict: Funds data
        """
        if not self.fyers:
            logger.error("Fyers client not initialized")
            return None
        
        try:
            response = self.fyers.funds()
            logger.info("Funds retrieved successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching funds: {e}")
            return None
    
    def is_authenticated(self):
        """
        Check if user is authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.access_token is not None and self.fyers is not None
    
    def logout(self):
        """
        Clear authentication state
        """
        self.access_token = None
        self.fyers = None
        logger.info("Logged out successfully")
    
    def validate_credentials(self):
        """
        Validate that API credentials are set
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if not self.client_id or not self.secret_key:
            logger.error("API credentials not set")
            return False
        
        if len(self.client_id) < 10 or len(self.secret_key) < 10:
            logger.error("API credentials appear to be invalid (too short)")
            return False
        
        return True
