# Stock Screener

A Python + Flask project that downloads stock market data, screens for breakout setups, and displays the results in a browser. The project is designed to scan a list of U.S. tickers, apply technical conditions, and then surface the strongest candidates in a simple dashboard.

## What this project does

The workflow is:

1. Read a list of stock tickers from `tickers/us_sector_tickers.csv`
2. Pull historical market data using Yahoo Finance (`yfinance`)
3. Evaluate breakout conditions such as:
   - 50-day moving average trend
   - 150-day moving average support
   - volume surge vs recent average
   - RSI momentum condition
   - recent price breakout above prior highs
4. Save qualifying results to `final.csv`
5. Show the results in a Flask web app

## Project structure

```text
StockScreenerProject/
├── StockScreener.py            # Flask app entry point
├── analyze.py                  # Breakout analysis logic
├── download_stock_data.py      # Downloads stock price history
├── final.csv                   # Generated output file (created after analysis)
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Ignores local secrets and generated data
├── stock_data/                # Folder containing per-ticker CSV files
├── templates/
│   ├── home.html               # Landing page
│   └── results.html            # Results dashboard
├── tickers/
│   └── us_sector_tickers.csv   # Ticker list used by the screener
└── venv/                      # Local virtual environment (if created)
```

## Requirements

- Python 3.10+
- pip
- Internet access to download market data from Yahoo Finance
- Optional: an EODHD API token if you choose to extend the data source setup

## Setup

### 1) Clone the repository

```bash
git clone https://github.com/anum-349/StockScreenerProject.git
cd StockScreenerProject
```

### 2) Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create a local environment file

Copy the example file and fill in any values you need:

```bash
copy .env.example .env
```

or on macOS/Linux:

```bash
cp .env.example .env
```

Example values are provided in `.env.example`.

### 5) Prepare the ticker list

The project expects a CSV file at `tickers/us_sector_tickers.csv`.

Example format:

```csv
Ticker,Sector,Exchange
AAPL,Technology,NASDAQ
MSFT,Technology,NASDAQ
NVDA,Technology,NASDAQ
```

If the folder does not exist, create it first:

```bash
mkdir tickers
```

## Run the project

### Download market data

```bash
python download_stock_data.py
```

This will save one CSV file per ticker under `stock_data/`.

### Run the analysis

```bash
python analyze.py
```

This reads the historical data files, applies the breakout logic, and creates or updates `final.csv`.

### Start the Flask app

```bash
python StockScreener.py
```

Then open one of these URLs in your browser:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/results`

## Notes about the data source

The project currently uses `yfinance` to pull daily market history, and the scripts also include an EODHD token placeholder for exchange metadata or future expansion. If you want to use a different data provider, update the relevant code in `download_stock_data.py` and `analyze.py`.

## Output

After analysis, the project writes a `final.csv` file containing rows like:

- Ticker
- Sector
- TradingView link
- Days since breakout
- Percentage above the 50-day moving average
- Breakout flag
- Score

The web app renders this output in `templates/results.html`.

## Troubleshooting

- If you see `No result file found`, run `python download_stock_data.py` and `python analyze.py` first.
- If Yahoo Finance fails, check that your internet connection is active and that the tickers in `tickers/us_sector_tickers.csv` are valid.
- If a ticker does not download, the script will skip it and continue to the next entry.

## License

This project is provided as-is for educational and personal stock screening experiments.
