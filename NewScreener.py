import pandas as pd
import requests
import json
import yfinance as yf
import datetime as dt
import os
import time
import traceback
from flask import render_template, jsonify, Flask, request
import logging
from bs4 import BeautifulSoup

from datetime import datetime
import pytz
app = Flask(__name__)
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

# Create stock_data folder if it doesn't exist
if not os.path.exists(stock_data_path):
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

        #df.columns = df.columns.droplevel(-1)

        # Save the formatted data to CSV
        df.to_csv(os.path.join(stock_data_path, f'{ticker}.csv'), index=False)

        # Calculate additional stock return data
        df['Pct Change'] = df['Adj Close'].pct_change()
        stock_return = (df['Pct Change'] + 1).cumprod().iloc[-1]
        return ticker, stock_return
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

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
    if not os.path.exists("final.csv"):
        breakouts_final.to_csv("final.csv", index=False)
    else:
        breakouts_final.to_csv("final.csv", mode='a', header=False, index=False)

tickers_df = pd.read_csv('us_sector_tickers.csv')
#tickers = tickers_df['Ticker'].tolist()
#for tick in tickers:
#    fetch_stock_data(tick)

sector_data={}

sector_tickers_df = pd.read_csv(f"us_sector_tickers.csv")
ticker = sector_tickers_df['Ticker'].tolist()
sector = sector_tickers_df['Sector'].tolist()
exchange = sector_tickers_df['Exchange'].tolist()


@app.route('/Analyze_Sector_A')
def Analyze():
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


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['GET'])
def result():
    if not os.path.isfile('final.csv'):
        return "No result file found"
    df = pd.read_csv('final.csv')
    data = df.to_dict(orient='records')  # Convert DataFrame to list of dicts
    return render_template('results.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)