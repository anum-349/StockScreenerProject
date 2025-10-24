# 📈 Stock Breakout Analysis and Visualization System

> *A Flask-based web application for analyzing U.S. stock market breakouts using technical indicators and API-driven financial data.*

---

## 🧭 Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [System Workflow](#system-workflow)
* [Installation](#installation)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Output](#output)

---

## 🌍 Overview

This project is a **Stock Market Breakout Analysis System** built with **Python (Flask)** and **Yahoo Finance API (yfinance)**.
It identifies **potential breakout stocks** from different U.S. sectors by analyzing technical indicators such as **Simple Moving Averages (SMA)**, **Relative Strength Index (RSI)**, and **volume patterns**.

The system automatically fetches and processes stock data, applies **custom screener rules**, and generates a **final CSV report** (`final.csv`).
Users can then view results in a **web-based dashboard** powered by Flask.

---

## ✨ Features

* 🧾 **Automated Data Fetching:** Uses Yahoo Finance API (`yfinance`) to download historical data for selected tickers.
* 📊 **Breakout Screening:** Applies multiple indicators including:

  * 50-day and 150-day SMA crossovers
  * Volume surge (>1.5× 5-day average)
  * RSI-based momentum check
  * Price breakout above recent highs
* 💾 **Result Export:** Automatically generates a `final.csv` file with all screened breakout stocks.
* 🌐 **Web Interface:** Flask app displays all analysis results in an organized HTML table.
* 🔗 **TradingView Integration:** Each stock entry links directly to its **TradingView** chart for quick analysis.

---

## 🧰 Tech Stack

**Backend:**

* Python 3
* Flask
* Pandas
* yfinance
* Requests
* pytz

**Frontend:**

* HTML (Flask Templates)
* Jinja2 Rendering

**Data:**

* Yahoo Finance historical data
* U.S. Sector tickers (CSV file)

---

## ⚙️ System Workflow

1. **Data Collection:**

   * Loads ticker data from `us_sector_tickers.csv` (containing Ticker, Sector, Exchange).
   * Downloads 1-year historical data for each ticker.

2. **Analysis:**

   * Calculates SMAs, RSI, volume averages, and breakout indicators.
   * Filters stocks matching defined technical criteria.

3. **Result Generation:**

   * Stores breakout data in `final.csv`.

4. **Visualization:**

   * Flask web app (`home.html` & `results.html`) displays final stock analysis results in a tabular format.

---

## 🖥️ Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/anum-349/StockScreenerProject.git
   cd StockScreenerProject
   ```

2. **Install Required Libraries:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Tickers:**

   * Place your file `us_sector_tickers.csv` inside the `/tickers/` folder.
   * Format:

     ```csv
     Ticker,Sector,Exchange
     AAPL,Technology,NASDAQ
     MSFT,Technology,NASDAQ
     ```

4. **Run the Analyzer:**

   ```bash
   python analyze.py
   ```

5. **Start the Flask Server:**

   ```bash
   python StockScreener.py
   ```

6. **View Results:**

   * Open your browser and go to 👉 `http://127.0.0.1:5000/results`

---

## 📁 Project Structure

```
Stock-Breakout-Analysis/
├── StockScreener.py            # Flask web interface
├── analyze.py                  # Core analysis logic
├── final.csv                   # Generated results
├── tickers/
│   └── us_sector_tickers.csv   # Ticker list by sector
├── templates/
│   ├── home.html               # Landing page
│   └── results.html            # Results display page
└── requirements.txt            # Project dependencies
```

---

## 📊 Output

Each row in `final.csv` and the Flask dashboard contains:

| Ticker | Sector     | TradingView Link                                                      | Days Since Breakout | % Above 50 MA | Breakout | Score |
| ------ | ---------- | --------------------------------------------------------------------- | ------------------- | ------------- | -------- | ----- |
| AAPL   | Technology | [View Chart](https://www.tradingview.com/chart/?symbol=NASDAQ%3AAAPL) | 2                   | 4.32%         | ✅        | 100   |
