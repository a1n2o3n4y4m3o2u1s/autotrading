# Auto Trading Bot (Bybit Linear Perpetuals)



This Python-based automated trading bot connects to the Bybit Unified Trading API to analyze perpetual futures, test multiple trading strategies, and execute trades automatically based on the most profitable parameters.

It leverages historical OHLC data to dynamically identify high-probability setups and place trades with optimal take-profit (TP) and stop-loss (SL) configurations.

## Features

• Automated daily trading using the schedule library  
• Backtesting engine that evaluates 10,000+ TP/SL combinations  
• Dynamic strategy selection based on expected value optimization  
• Leverage and position sizing calculated from wallet balance  
• Bybit API integration via pybit.unified_trading  
• Automatic market scanning for new perpetual coins  
• Daily execution of trading logic at midnight UTC  

## Project Structure

auto_trading_bot/
│
├── autotrading.py           # Core script containing trading logic
├── README.md         # Project documentation
└── LICENCE

## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/auto_trading_bot.git
   cd auto_trading_bot

2. Install dependencies:
   pip install pybit schedule

## Setup

1. Generate Bybit API Keys  
   Go to Bybit API Management → Create an API key with Read and Trade permissions.  
   Copy your API key and secret.

2. Configure API Credentials  
   Open main.py and fill in your credentials:
   session = HTTP(testnet=False, api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")

3. (Optional) To test safely, set testnet=True and use Bybit’s testnet API.

## How It Works

1. Data Collection  
   Fetches all linear perpetual instruments and retrieves daily OHLC data for each.

2. Backtesting  
   Iterates through combinations of Take Profit (TP) and Stop Loss (SL) percentages.  
   Simulates entries and exits using historical data.  
   Calculates win rate, maximum open trades, and expected value (EV).  
   Selects the best-performing strategy based on EV.

3. Trade Execution  
   Detects bearish reversal setups and calculates leverage, quantity, and target prices.  
   Places market sell orders with TP and SL.

4. Scheduling  
   The bot runs automatically every day at UTC midnight (new daily candle):
   schedule.every().day.at("00:00").do(autoTrading)

## Example Output

{'tp': 15, 'sl': 5, 'maxOpenTrades': 3, 'winRate': 0.72, 'expectedValue': 0.084}
[{'symbol': 'BTCUSDT', 'tpPrice': 63000.0, 'slPrice': 67000.0}, ...]

## Disclaimer

This project is for educational and research purposes only.  
Trading cryptocurrencies involves significant financial risk — past performance does not guarantee future results.  
Use Bybit Testnet before deploying real funds.

## License

This project is licensed under the MIT License.  
See the [LICENSE](./LICENSE) file for details.

## AI Disclaimer

Large portions of this README and some accompanying descriptions were generated or adapted with the help of AI tools.

