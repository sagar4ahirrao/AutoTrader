"""
Fyers Algo Trading Application
Streamlit-based UI for automated trading with Fyers API
"""
import streamlit as st
import logging
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Import modules
import config
from auth.fyers_auth import FyersAuth
from api.fyers_client import FyersClient
from api.market_data import MarketData
from strategies.ema_options import EMAOptionsStrategy
from webhook.server import WebhookServer
from utils.helpers import format_price, format_pnl, is_market_open

# Setup logging
logger = config.setup_logging()

# Page configuration
st.set_page_config(
    page_title="Fyers Algo Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'fyers_auth' not in st.session_state:
    st.session_state.fyers_auth = None
if 'fyers_client' not in st.session_state:
    st.session_state.fyers_client = None
if 'market_data' not in st.session_state:
    st.session_state.market_data = None
if 'strategy' not in st.session_state:
    st.session_state.strategy = None
if 'webhook_server' not in st.session_state:
    st.session_state.webhook_server = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None


def initialize_components():
    """Initialize trading components after authentication"""
    if st.session_state.fyers_auth and st.session_state.fyers_auth.fyers:
        # Initialize API client
        if not st.session_state.fyers_client:
            st.session_state.fyers_client = FyersClient(st.session_state.fyers_auth.fyers)
        
        # Initialize market data
        if not st.session_state.market_data:
            st.session_state.market_data = MarketData(st.session_state.fyers_auth.fyers)


def login_page():
    """Login page for Fyers OAuth authentication"""
    st.markdown('<div class="main-header">🔐 Fyers Login</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to Fyers Algo Trading Platform
    
    This application provides automated trading capabilities with:
    - **OAuth Authentication** with Fyers
    - **EMA-based Options Strategy**
    - **Webhook Support** for TradingView
    - **Real-time Monitoring** and Analytics
    
    ---
    """)
    
    # Credentials input
    st.subheader("📋 API Credentials")
    st.markdown("Get your credentials from [Fyers API Dashboard](https://myapi.fyers.in/dashboard/)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_id = st.text_input("Client ID (App ID)", value=config.FYERS_CLIENT_ID, type="password")
    
    with col2:
        secret_key = st.text_input("Secret Key", value=config.FYERS_SECRET_KEY, type="password")
    
    redirect_url = st.text_input("Redirect URL", value=config.FYERS_REDIRECT_URL)
    
    st.markdown("---")
    
    # Authentication flow
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Login with Fyers", use_container_width=True, type="primary"):
            if not client_id or not secret_key:
                st.error("Please enter both Client ID and Secret Key")
            else:
                try:
                    # Initialize auth
                    auth = FyersAuth(client_id, secret_key, redirect_url)
                    
                    if not auth.validate_credentials():
                        st.error("Invalid credentials format")
                        return
                    
                    # Generate auth URL
                    auth_url = auth.generate_auth_url()
                    
                    st.session_state.fyers_auth = auth
                    st.session_state.auth_url = auth_url
                    
                    st.success("✅ Authentication URL generated!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Login error: {e}")
    
    # Show auth URL if generated
    if hasattr(st.session_state, 'auth_url'):
        st.markdown("---")
        st.subheader("🔗 Step 2: Complete Authentication")
        
        st.markdown(f"""
        <div class="warning-box">
        <strong>Click the link below to authorize the application:</strong><br>
        <a href="{st.session_state.auth_url}" target="_blank">{st.session_state.auth_url}</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("After authorization, copy the **full redirect URL** from your browser:")
        
        redirect_response = st.text_input("Paste the redirect URL here:", key="redirect_url")
        
        if st.button("Generate Access Token", type="primary"):
            if not redirect_response:
                st.error("Please paste the redirect URL")
            else:
                try:
                    # Extract auth code
                    auth_code = st.session_state.fyers_auth.extract_auth_code(redirect_response)
                    
                    if not auth_code:
                        st.error("Could not extract authorization code from URL")
                        return
                    
                    # Generate access token
                    access_token = st.session_state.fyers_auth.generate_access_token(auth_code)
                    
                    if access_token:
                        st.session_state.access_token = access_token
                        st.session_state.authenticated = True
                        
                        st.success("🎉 Successfully authenticated!")
                        st.balloons()
                        
                        # Initialize components
                        initialize_components()
                        
                        st.rerun()
                    else:
                        st.error("Failed to generate access token")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Token generation error: {e}")


def dashboard_page():
    """Main dashboard page"""
    st.markdown('<div class="main-header">📊 Trading Dashboard</div>', unsafe_allow_html=True)
    
    # Account info
    try:
        profile = st.session_state.fyers_auth.get_profile()
        funds = st.session_state.fyers_auth.get_funds()
        
        if profile and profile.get('s') == 'ok':
            profile_data = profile.get('data', {})
            st.markdown(f"### Welcome, {profile_data.get('name', 'Trader')}!")
        
        # Display funds
        col1, col2, col3, col4 = st.columns(4)
        
        if funds and funds.get('s') == 'ok':
            fund_data = funds.get('fund_limit', [{}])[0]
            
            with col1:
                st.metric("Available Balance", format_price(fund_data.get('equityAmount', 0)))
            with col2:
                st.metric("Used Margin", format_price(fund_data.get('utilized_amount', 0)))
            with col3:
                st.metric("Collateral", format_price(fund_data.get('collateral', 0)))
            with col4:
                market_status = "🟢 Open" if is_market_open() else "🔴 Closed"
                st.metric("Market Status", market_status)
        
    except Exception as e:
        st.error(f"Error fetching account info: {e}")
        logger.error(f"Dashboard error: {e}")
    
    st.markdown("---")
    
    # Positions and Orders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Positions")
        try:
            positions_response = st.session_state.fyers_client.get_positions()
            
            if positions_response and positions_response.get('s') == 'ok':
                positions = positions_response.get('netPositions', [])
                
                if positions:
                    positions_df = pd.DataFrame(positions)
                    st.dataframe(positions_df[['symbol', 'netQty', 'avgPrice', 'ltp', 'pl']] if len(positions_df.columns) > 0 else positions_df)
                else:
                    st.info("No open positions")
            else:
                st.warning("Could not fetch positions")
                
        except Exception as e:
            st.error(f"Error fetching positions: {e}")
    
    with col2:
        st.subheader("📋 Orders")
        try:
            orders_response = st.session_state.fyers_client.get_orders()
            
            if orders_response and orders_response.get('s') == 'ok':
                orders = orders_response.get('orderBook', [])
                
                if orders:
                    orders_df = pd.DataFrame(orders)
                    st.dataframe(orders_df[['symbol', 'qty', 'type', 'status', 'orderDateTime']] if len(orders_df.columns) > 0 else orders_df)
                else:
                    st.info("No orders today")
            else:
                st.warning("Could not fetch orders")
                
        except Exception as e:
            st.error(f"Error fetching orders: {e}")


def strategy_page():
    """Strategy configuration and execution page"""
    st.markdown('<div class="main-header">⚡ Strategy Configuration</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### EMA Crossover Options Strategy
    
    This strategy uses Exponential Moving Averages (EMA) to generate trading signals:
    - **Bullish Signal**: Fast EMA crosses above Slow EMA → Buy Call Option
    - **Bearish Signal**: Fast EMA crosses below Slow EMA → Buy Put Option
    """)
    
    st.markdown("---")
    
    # Strategy Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Strategy Parameters")
        
        underlying = st.selectbox(
            "Underlying Symbol",
            options=["NIFTY", "BANKNIFTY"],
            index=0
        )
        
        underlying_symbol = config.NIFTY_SYMBOL if underlying == "NIFTY" else config.BANKNIFTY_SYMBOL
        
        fast_ema = st.number_input("Fast EMA Period", min_value=3, max_value=50, value=config.DEFAULT_FAST_EMA)
        slow_ema = st.number_input("Slow EMA Period", min_value=10, max_value=200, value=config.DEFAULT_SLOW_EMA)
        
        timeframe = st.selectbox("Timeframe", options=["1min", "5min", "15min"], index=1)
        
    with col2:
        st.subheader("💰 Risk Management")
        
        position_size = st.number_input("Position Size (Lots)", min_value=1, max_value=100, value=config.DEFAULT_POSITION_SIZE)
        stop_loss_pct = st.number_input("Stop Loss %", min_value=0.5, max_value=10.0, value=config.DEFAULT_STOP_LOSS_PCT, step=0.5)
        target_pct = st.number_input("Target %", min_value=1.0, max_value=20.0, value=config.DEFAULT_TARGET_PCT, step=0.5)
        
        trading_mode = st.radio("Trading Mode", options=["PAPER", "LIVE"], index=0 if config.TRADING_MODE == "PAPER" else 1)
    
    st.markdown("---")
    
    # Initialize Strategy
    if st.button("Initialize Strategy", type="primary"):
        try:
            strategy_config = {
                'underlying_symbol': underlying_symbol,
                'fast_ema_period': fast_ema,
                'slow_ema_period': slow_ema,
                'timeframe': config.CANDLE_TIMEFRAMES.get(timeframe, '5'),
                'position_size': position_size,
                'stop_loss_pct': stop_loss_pct,
                'target_pct': target_pct
            }
            
            # Update trading mode
            config.TRADING_MODE = trading_mode
            
            # Initialize strategy
            strategy = EMAOptionsStrategy(
                st.session_state.fyers_client,
                st.session_state.market_data,
                strategy_config
            )
            
            st.session_state.strategy = strategy
            
            st.success("✅ Strategy initialized successfully!")
            
        except Exception as e:
            st.error(f"❌ Error initializing strategy: {e}")
            logger.error(f"Strategy init error: {e}")
    
    # Strategy Control
    if st.session_state.strategy:
        st.markdown("---")
        st.subheader("🎮 Strategy Control")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("▶️ Start Strategy", use_container_width=True):
                st.session_state.strategy.start()
                st.success("Strategy started!")
        
        with col2:
            if st.button("⏸️ Stop Strategy", use_container_width=True):
                st.session_state.strategy.stop()
                st.warning("Strategy stopped!")
        
        with col3:
            if st.button("🔄 Run Once", use_container_width=True):
                result = st.session_state.strategy.run_iteration()
                st.json(result)
        
        with col4:
            if st.button("🚪 Exit All Positions", use_container_width=True):
                st.session_state.strategy.close_all_positions()
                st.info("All positions closed!")
        
        # Strategy Status
        status = st.session_state.strategy.get_status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "🟢 Running" if status['is_running'] else "🔴 Stopped")
        with col2:
            st.metric("Active Positions", status['positions'])
        with col3:
            st.metric("Total Trades", status['total_trades'])
        
        # Trade History
        if status['total_trades'] > 0:
            st.markdown("---")
            st.subheader("📜 Trade History")
            
            trades = st.session_state.strategy.get_trade_history(limit=10)
            trades_df = pd.DataFrame(trades)
            st.dataframe(trades_df, use_container_width=True)


def webhook_page():
    """Webhook configuration page"""
    st.markdown('<div class="main-header">🔗 Webhook Configuration</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### TradingView Webhook Integration
    
    Receive trading signals from TradingView alerts and execute them automatically.
    """)
    
    # Initialize webhook server
    if not st.session_state.webhook_server:
        st.session_state.webhook_server = WebhookServer()
        
        # Set trade callback
        def webhook_trade_callback(webhook_data):
            logger.info(f"Webhook callback triggered: {webhook_data}")
            # Here you would execute the trade
            # For demo, just log it
            return {"status": "received", "mode": config.TRADING_MODE}
        
        st.session_state.webhook_server.set_trade_callback(webhook_trade_callback)
    
    st.markdown("---")
    
    # Server Control
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Webhook Server", use_container_width=True, type="primary"):
            st.session_state.webhook_server.start()
            st.success("Webhook server started!")
    
    with col2:
        if st.button("⏹️ Stop Webhook Server", use_container_width=True):
            st.session_state.webhook_server.stop()
            st.warning("Webhook server stopped!")
    
    # Webhook URL
    st.markdown("---")
    st.subheader("📡 Webhook URL")
    
    webhook_url = st.session_state.webhook_server.get_webhook_url()
    
    st.code(webhook_url, language="text")
    
    st.markdown(f"""
    <div class="success-box">
    <strong>Use this URL in your TradingView alerts!</strong><br>
    Copy the URL above and paste it in the "Webhook URL" field when creating TradingView alerts.
    </div>
    """, unsafe_allow_html=True)
    
    # Security Token
    st.markdown("---")
    st.subheader("🔐 Security Token")
    
    st.code(config.WEBHOOK_TOKEN, language="text")
    
    st.markdown("""
    <div class="warning-box">
    <strong>Important:</strong> Include this token in your webhook payload for authentication.
    </div>
    """, unsafe_allow_html=True)
    
    # Sample Payload
    st.markdown("---")
    st.subheader("📝 Sample TradingView Alert Configuration")
    
    sample_payload = st.session_state.webhook_server.test_webhook()
    
    st.json(sample_payload)
    
    st.markdown("""
    **TradingView Alert Message:**
    ```json
    {
        "token": "your_webhook_secret_token_here",
        "action": "BUY",
        "symbol": "NSE:SBIN-EQ",
        "quantity": 1,
        "order_type": "MARKET",
        "price": 0
    }
    ```
    """)
    
    # Webhook Logs
    st.markdown("---")
    st.subheader("📊 Recent Webhook Logs")
    
    if st.button("🔄 Refresh Logs"):
        st.rerun()
    
    logs = st.session_state.webhook_server.get_logs(limit=20)
    
    if logs:
        logs_df = pd.DataFrame(logs)
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No webhook requests received yet")


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/368px-Google_2015_logo.svg.png", width=100)
        st.markdown("# 📈 Fyers Algo")
        st.markdown("---")
        
        if st.session_state.authenticated:
            page = st.radio(
                "Navigation",
                options=["Dashboard", "Strategy", "Webhook", "Logout"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.markdown("### ℹ️ Info")
            st.markdown(f"**Mode:** {config.TRADING_MODE}")
            st.markdown(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
            
            if page == "Logout":
                st.session_state.authenticated = False
                st.session_state.fyers_auth = None
                st.session_state.access_token = None
                st.rerun()
        else:
            st.markdown("### 🔐 Please Login")
            page = "Login"
    
    # Main content
    if not st.session_state.authenticated:
        login_page()
    else:
        if page == "Dashboard":
            dashboard_page()
        elif page == "Strategy":
            strategy_page()
        elif page == "Webhook":
            webhook_page()


if __name__ == "__main__":
    main()
