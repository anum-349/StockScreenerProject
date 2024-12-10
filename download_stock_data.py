import pandas as pd
import requests
import yfinance as yf
import datetime as dt
import os

# Replace with your API key
api_key = '672dfdfef10c42.49990560'  # Use your actual API key here
exchange_code = 'US'  # Replace this with a valid exchange code
base_url = f'https://eodhd.com/api/exchange-symbol-list/{exchange_code}'

response = requests.get(f"{base_url}?api_token={api_key}&fmt=json")

# Set up paths for final CSV and stock data
base_path = os.path.dirname(os.path.abspath(__file__))
stock_data_path = os.path.join(base_path, 'stock_data')
tickers_path = os.path.join(base_path, 'tickers')
us_sector_tickers_file =  os.path.join(tickers_path, 'us_sector_tickers.csv')

sector_tickers_df = pd.read_csv(us_sector_tickers_file)
ticker = sector_tickers_df['Ticker'].tolist()
sector = sector_tickers_df['Sector'].tolist()
exchange = sector_tickers_df['Exchange'].tolist()

# Create stock_data folder if it doesn't exist
if os.path.exists(stock_data_path):
    os.remove(stock_data_path)
    print("Removed")
os.makedirs(stock_data_path)

def load_data_from_csv(ticker):
    csv_path = os.path.join(stock_data_path, f'{ticker}.csv')
    if os.path.exists(csv_path):
        sector_tickers_df = pd.read_csv(csv_path)
        return sector_tickers_df['Ticker'].tolist()
    else:
        print("CSV file not found.")
        return []

start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

def fetch_stock_data(ticker):
    try:
        print(ticker)
        df = yf.download(ticker, start=start, end=end)
        if df.empty:
            return None, None

        # Ensure columns are in the right format and add missing ones if necessary
        df['Date'] = df.index
        expected_columns = ['Date', 'Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = float('nan')  # Add missing columns as NaN if they don’t exist

        df = df[expected_columns]

        df.columns = df.columns.droplevel(-1)

        # Save the formatted data to CSV
        df.to_csv(os.path.join(stock_data_path, f'{ticker}.csv'), index=False)

        # Calculate additional stock return data
        df['Pct Change'] = df['Adj Close'].pct_change()
        stock_return = (df['Pct Change'] + 1).cumprod().iloc[-1]
        return ticker, stock_return
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

for tick in ticker:
    fetch_stock_data(tick)