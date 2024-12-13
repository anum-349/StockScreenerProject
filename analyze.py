import pandas as pd
import requests
import datetime as dt
import os
import logging
from datetime import datetime
import pytz

# Replace with your API key
api_key = '672dfdfef10c42.49990560'  # Use your actual API key here
exchange_code = 'US'  # Replace this with a valid exchange code
base_url = f'https://eodhd.com/api/exchange-symbol-list/{exchange_code}'

response = requests.get(f"{base_url}?api_token={api_key}&fmt=json")

ticker=[]
sector=[]
exchange=[]

def get_trading_Link(tick):
    for tikr, exch in zip(ticker, exchange):
        if tikr == tick:
            return f"https://www.tradingview.com/chart/?symbol={exch}%3A{tikr}"

# Set up paths for final CSV and stock data
base_path = os.path.dirname(os.path.abspath(__file__))
final_path = os.path.join(base_path, 'final.csv')
stock_data_path = os.path.join(base_path, 'stock_data')
tickers_path = os.path.join(base_path, 'tickers')
us_sector_tickers_file =  os.path.join(tickers_path, 'us_sector_tickers.csv')

# Create stock_data folder if it doesn't exist
if not os.path.exists(stock_data_path):
    os.makedirs(stock_data_path)

start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()


def analyze(ticker, sector):
    tradingview_link = get_trading_Link(ticker)
    file_path = os.path.join(stock_data_path, f"{ticker}.csv")
    if not os.path.isfile(file_path):
        return
    historical_data = pd.read_csv(file_path)
    # Calculate the required moving averages
    historical_data['50_SMA'] = historical_data['Close'].rolling(window=50).mean()
    historical_data['150_SMA'] = historical_data['Close'].rolling(window=150).mean()

    # Calculate the 5-day average volume
    historical_data['5_Day_Avg_Vol'] = historical_data['Volume'].rolling(window=5).mean()

    # Apply Breakout Screener Rules
    historical_data['Breakout'] = (
            (historical_data['Volume'] > 100000) &  # Volume > 100,000
            (historical_data['Close'] > historical_data['150_SMA']) &  # Close > 150 SMA
            (historical_data['Close'].shift(1) <= historical_data['50_SMA'].shift(1)) &  # Prior day's close below 50 SMA
            (historical_data['Close'] > historical_data['50_SMA']) &  # Today's close above 50 SMA (cross over)
            (historical_data['Volume'] > 1.5 * historical_data['5_Day_Avg_Vol'])  # Volume 50% greater than 5-day avg
    )

    # Calculate RSI to implement Mansfield RSI conditions
    delta = historical_data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    historical_data['RSI'] = 100 - (100 / (1 + rs))

    # Mansfield RSI condition: Check if RSI is higher than the previous day
    historical_data['Mansfield_RSI_Higher'] = historical_data['RSI'] > historical_data['RSI'].shift(1)

    # Recent high: Highest closing price over the last 10 days
    historical_data['10_Day_High'] = historical_data['Close'].rolling(window=10).max()
    historical_data['Above_Recent_High'] = historical_data['Close'] > historical_data['10_Day_High'].shift(1)

    # Combine all breakout conditions
    historical_data['Breakout'] &= historical_data['Mansfield_RSI_Higher'] & historical_data['Above_Recent_High']
    historical_data['Breakout Date'] = historical_data.index.where(historical_data['Breakout'])
    historical_data['Breakout Date'] = pd.to_datetime(historical_data['Date'])
    current_date = datetime.now(pytz.timezone("America/New_York"))
    historical_data['Days_Since_Breakout'] = (current_date - historical_data['Breakout Date']).dt.days
    historical_data['Days_Since_Breakout'] = historical_data['Days_Since_Breakout'].fillna(0).astype(int)

    # Filter for breakouts that happened in the last 5 days
    breakouts = historical_data[(historical_data['Breakout']) & (historical_data['Days_Since_Breakout'] <= 5)].copy()

    # Calculate percentage above 50 SMA
    breakouts['Pct_Above_50MA'] = ((breakouts['Close'] - breakouts['50_SMA']) / breakouts['50_SMA']) * 100

    # Set Score (example scoring based on your needs)
    breakouts['Score'] = 100  # Placeholder for actual scoring criteria

    # Add necessary columns for final output
    breakouts['Ticker'] = ticker
    breakouts['Sector'] = sector
    breakouts['TradingView_Link'] = tradingview_link

    # Select relevant columns for final output
    breakouts_final = breakouts[
        ['Ticker', 'Sector', 'TradingView_Link', 'Days_Since_Breakout', 'Pct_Above_50MA', 'Breakout', 'Score']
    ]

    # Save breakout data to 'final.csv', appending if the file already exists
    if not os.path.exists(final_path):
        breakouts_final.to_csv(final_path, index=False)
    else:
        breakouts_final.to_csv(final_path, mode='a', header=False, index=False)

tickers_df = pd.read_csv(us_sector_tickers_file)

sector_data={}

sector_tickers_df = pd.read_csv(us_sector_tickers_file)
ticker = sector_tickers_df['Ticker'].tolist()
sector = sector_tickers_df['Sector'].tolist()
exchange = sector_tickers_df['Exchange'].tolist()


def analyze_call():
    try:
        for tick, sect in zip(ticker, sector):
            analyze(tick, sect)
            print(f"Analayzed {tick}")
            # Return a success message
        return f"Data for sector loaded successfully."
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        # Optional: re-raise the exception if you want it to show up as an error
        raise

if os.path.exists(final_path):
    os.remove(final_path)
    print("Removed")

analyze_call()