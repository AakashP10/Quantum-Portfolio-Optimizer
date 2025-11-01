from flask import Flask, render_template, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd

app = Flask(__name__)

COMPANY_TICKER_MAP = {
    "Apple Inc.": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Alphabet Inc. (Google)": "GOOG",
    "Amazon.com Inc.": "AMZN",
    "Tesla Inc.": "TSLA",
    "Meta Platforms Inc.": "META",
    "NVIDIA Corporation": "NVDA",
    "Netflix Inc.": "NFLX",
    "Intel Corporation": "INTC",
    "Walmart Inc.": "WMT",
    "Bank of America": "BAC",
    "JPMorgan Chase & Co.": "JPM",
    "Goldman Sachs Group Inc.": "GS",
    "Exxon Mobil Corporation": "XOM",
    "Chevron Corporation": "CVX",
    "Pfizer Inc.": "PFE",
    "Johnson & Johnson": "JNJ",
    "Procter & Gamble Co.": "PG",
    "The Coca-Cola Company": "KO",
    "PepsiCo Inc.": "PEP"
}

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        companies = data.get("companies", [])
        k = int(data.get("k", 20))
        risk_factor = float(data.get("lambda", 2.7))

        if not companies:
            return jsonify({"error": "No companies selected."}), 400

        tickers = [COMPANY_TICKER_MAP.get(name.strip()) for name in companies if COMPANY_TICKER_MAP.get(name.strip())]
        if not tickers:
            return jsonify({"error": "No valid tickers found."}), 400

        stock_data = yf.download(tickers, period="1y", group_by="ticker", auto_adjust=True, threads=True)

        if stock_data.empty:
            return jsonify({"error": "No valid stock data fetched."}), 500

        try:
            adj_close = pd.concat([stock_data[ticker]["Close"] for ticker in tickers], axis=1)
            adj_close.columns = tickers
        except Exception as e:
            return jsonify({"error": f"Data processing error: {str(e)}"}), 500

        returns = adj_close.pct_change().dropna()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        weights = np.ones(len(mean_returns)) / len(mean_returns)
        expected_return = float(np.dot(weights, mean_returns))
        risk = float(np.dot(weights.T, np.dot(cov_matrix, weights)))

        latest_ticker = tickers[0]
        latest_data = yf.download(latest_ticker, period="5d")

        if latest_data.empty:
            return jsonify({"error": f"No data available for {latest_ticker}."}), 500

        latest_row = latest_data.iloc[-1]
        open_price = float(latest_row.get("Open", 0))
        high_price = float(latest_row.get("High", 0))
        low_price = float(latest_row.get("Low", 0))
        close_price = float(latest_row.get("Close", 0))
        volume = int(latest_row.get("Volume", 0))

    
        summary_table = [
            {"Term": "Selected Assets", "Meaning": "Stocks chosen for optimization"},
            {"Term": "Open", "Meaning": "Price of the stock when the market opened today"},
            {"Term": "High", "Meaning": "Highest price the stock reached today"},
            {"Term": "Low", "Meaning": "Lowest price the stock fell to today"},
            {"Term": "Close", "Meaning": "Price of the stock when the market closed today"},
            {"Term": "Volume", "Meaning": "Number of shares traded today"},
            {"Term": "Expected Return", "Meaning": "Average daily return from the selected portfolio"},
            {"Term": "Risk", "Meaning": "Price fluctuation or volatility of the portfolio"},
        ]

        return jsonify({
            "selected_assets": ", ".join(companies),
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume,
            "expected_return": expected_return,
            "risk": risk,
            "summary": summary_table
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
