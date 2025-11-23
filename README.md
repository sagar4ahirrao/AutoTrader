# Fyers Algo Trading Application

A comprehensive full-stack algorithmic trading application for Fyers using Python and Streamlit. This application provides OAuth authentication, EMA-based options trading strategies, and webhook support for TradingView integration.

## 🌟 Features

- **🔐 Secure OAuth Authentication** - Automated login with Fyers API
- **📊 Real-time Dashboard** - Monitor positions, orders, and account balance
- **⚡ EMA Options Strategy** - Automated EMA crossover-based options trading
- **🔗 Webhook Support** - Integration with TradingView alerts
- **📈 Live Market Data** - Real-time quotes and historical data
- **🎮 Strategy Control** - Start, stop, and monitor strategies
- **📝 Trade Logging** - Complete audit trail of all trades
- **🎯 Risk Management** - Configurable stop-loss and target levels

## 📋 Prerequisites

- Python 3.8 or higher
- Active Fyers trading account
- Fyers API credentials (Client ID and Secret Key)

## 🚀 Quick Start

### 1. Clone or Download

Download this application to your local machine.

### 2. Install Dependencies

```bash
cd d:\cams2csv\AutoTrader
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```bash
copy .env.example .env
```

Edit `.env` file:
```env
FYERS_CLIENT_ID=your_client_id_here
FYERS_SECRET_KEY=your_secret_key_here
FYERS_REDIRECT_URL=http://localhost:8501
WEBHOOK_PORT=5000
WEBHOOK_TOKEN=your_webhook_secret_token_here
```

### 4. Get Fyers API Credentials

1. Visit [Fyers API Dashboard](https://myapi.fyers.in/dashboard/)
2. Create a new app
3. Note down your **Client ID** and **Secret Key**
4. Set redirect URL to `http://localhost:8501`

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 User Guide

### Authentication

1. **Enter Credentials**: Input your Client ID, Secret Key, and Redirect URL
2. **Login**: Click "Login with Fyers" to generate authentication URL
3. **Authorize**: Click the generated link to authorize the application
4. **Complete**: Copy the redirect URL and paste it to generate access token

### Dashboard

- View account balance and margin
- Monitor active positions and P&L
- Check pending and executed orders
- See market status

### Strategy Configuration

1. **Select Underlying**: Choose NIFTY or BANKNIFTY
2. **Set EMA Periods**: Configure Fast EMA (default: 9) and Slow EMA (default: 21)
3. **Configure Risk**: Set position size, stop-loss %, and target %
4. **Choose Mode**: Select PAPER (demo) or LIVE trading
5. **Initialize**: Click "Initialize Strategy"
6. **Control**: Start, stop, or run strategy manually

### EMA Strategy Logic

- **Bullish Signal**: Fast EMA crosses above Slow EMA → Buy Call Option
- **Bearish Signal**: Fast EMA crosses below Slow EMA → Buy Put Option
- **Exit**: Opposite crossover or target/stop-loss hit

### Webhook Integration

1. **Start Server**: Click "Start Webhook Server" in the Webhook page
2. **Copy URL**: Copy the webhook URL displayed
3. **TradingView Setup**:
   - Create an alert in TradingView
   - Set webhook URL to the copied URL
   - Use the sample JSON payload format
   - Include your security token

**Sample TradingView Alert Message:**
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

## 🏗️ Project Structure

```
AutoTrader/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── auth/                      # Authentication
│   ├── __init__.py
│   └── fyers_auth.py         # OAuth implementation
│
├── api/                       # API clients
│   ├── __init__.py
│   ├── fyers_client.py       # Trading operations
│   └── market_data.py        # Market data fetching
│
├── strategies/                # Trading strategies
│   ├── __init__.py
│   ├── base_strategy.py      # Base strategy class
│   └── ema_options.py        # EMA strategy
│
├── webhook/                   # Webhook server
│   ├── __init__.py
│   └── server.py             # Flask server
│
└── utils/                     # Utilities
    ├── __init__.py
    ├── indicators.py         # Technical indicators
    └── helpers.py            # Helper functions
```

## ⚙️ Configuration

### Strategy Parameters

- **Fast EMA Period**: Short-term EMA (default: 9)
- **Slow EMA Period**: Long-term EMA (default: 21)
- **Timeframe**: Candle timeframe - 1min, 5min, 15min
- **Position Size**: Number of lots to trade
- **Stop Loss**: Stop-loss percentage (default: 2%)
- **Target**: Target profit percentage (default: 4%)

### Trading Modes

- **PAPER**: Demo mode - simulates trades without real execution
- **LIVE**: Live trading mode - executes real trades

> ⚠️ **Warning**: Always test strategies in PAPER mode first!

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Keep credentials private
2. **Use strong webhook tokens** - Generate random secure tokens
3. **Enable IP whitelisting** - Restrict webhook access (if deploying to server)
4. **Regular monitoring** - Check logs for unauthorized access
5. **Rotate tokens** - Change tokens periodically

## 📊 Technical Indicators

The application includes several technical indicators:

- **EMA** (Exponential Moving Average)
- **SMA** (Simple Moving Average)
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**

## 🐛 Troubleshooting

### Authentication Issues

- Ensure credentials are correct
- Check redirect URL matches exactly
- Verify API app is active in Fyers dashboard

### Strategy Not Running

- Check market hours (9:15 AM - 3:30 PM IST, Mon-Fri)
- Verify sufficient data for EMA calculation
- Check trading mode (PAPER vs LIVE)

### Webhook Not Receiving

- Ensure webhook server is started
- Verify port 5000 is not blocked
- Check webhook token in TradingView alert
- Review webhook logs for errors

### Installation Errors

```bash
# If fyers-apiv3 installation fails
pip install --upgrade pip
pip install fyers-apiv3 --no-cache-dir

# If pandas/numpy issues
pip install pandas numpy --upgrade
```

## 📝 Logging

Logs are saved to `trading_app.log` in the application directory. Check this file for detailed execution logs and errors.

## ⚠️ Risk Disclaimer

**IMPORTANT**: This software is for educational and demonstration purposes only.

- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Always use paper trading first before live trading
- Never trade with money you cannot afford to lose
- The developers are not responsible for any trading losses

## 🤝 Support

For issues related to:
- **Fyers API**: Contact [Fyers Support](https://fyers.in/contact/)
- **Application Bugs**: Check logs and error messages

## 📜 License

This project is provided as-is for educational purposes.

## 🔄 Version History

### Version 1.0 (Current)
- OAuth authentication
- EMA options strategy
- Webhook integration
- Real-time dashboard
- Paper trading support

## 🎯 Future Enhancements

Potential improvements for future versions:
- Multiple strategy support
- Advanced backtesting
- Strategy optimization
- Email/SMS notifications
- Database integration for trade history
- Advanced charting with indicators
- Multiple timeframe analysis

## 📚 Resources

- [Fyers API Documentation](https://api-docs.fyers.in/)
- [TradingView Webhooks](https://www.tradingview.com/support/solutions/43000529348-about-webhooks/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Happy Trading! 📈**

*Remember: Always trade responsibly and never risk more than you can afford to lose.*
