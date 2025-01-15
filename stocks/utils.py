import yfinance as yf


def fetch_stock_info(ticker):
    stock_data = []
    ticker = ticker.upper().strip()
    stock = yf.Ticker(ticker)
    stock_info = stock.history(period='1d')
    if not stock_info.empty:
        row = stock_info.iloc[-1]
        price = row['Close']
        previous_close = stock.info.get('previousClose', price)
        change = price - previous_close
        stock_data = {
            'ticker': ticker,
            'price': f"{row['Close']:.2f}",
            'high': f"{row['High']:.2f}",
            'low': f"{row['Low']:.2f}",
            'volume': f"{row['Volume']:.2f}",
            'previous_close': f"{previous_close:.2f}",
            'change': f"{change:.2f}",
            'change_percent': f"{(change / previous_close) * 100 if previous_close else 0 :.2f}",
            'date_time': row.name.strftime('%Y-%m-%d')
        }
    return stock_data