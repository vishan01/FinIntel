import yfinance as yf
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt



def fetch_top_stocks():
    top_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BRK-B', 'V', 'JNJ', 'WMT', 'JPM', 'PG', 'UNH', 'NVDA', 'HD', 'DIS', 'PYPL', 'MA', 'VZ', 'ADBE', 'NFLX', 'INTC', 'CMCSA', 'PFE', 'KO', 'PEP', 'T', 'MRK', 'ABT', 'CSCO', 'XOM', 'NKE', 'LLY', 'MCD', 'DHR', 'WFC', 'MDT', 'BMY', 'COST', 'NEE', 'META']
    stocks_data = []
    for ticker in top_stocks:
        stocks_data.append(fetch_stock_info(ticker))
    return stocks_data

def fetch_stock_info(ticker):
    stock_data = []
    ticker = ticker.upper().strip()
    stock = yf.Ticker(ticker)
    stock_info = stock.history(period='1d')
    if not stock_info.empty:
        row = stock_info.iloc[-1]
        price = row['Open']
        previous_close = stock_info.get('previousClose',row['Close'])
        change = price - previous_close
        stock_data = {
            'ticker': ticker,
            'price': round(row['Open'],2),
            'high': round(row['High'],2),
            'low': round(row['Low'],2),
            'volume': round(row['Volume'],2),
            'previous_close': round(previous_close,2),
            'change': round(change,2),
            'change_percent': round((change / previous_close) * 100 if previous_close else 0 ,2),
            'date_time': row.name.strftime('%Y-%m-%d')
        }
    return stock_data



import matplotlib.pyplot as plt


def plot_stocks(stocks_watchlist):
    yf_period   = "1mo"   # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    yf_interval = "1d"
    yf_returns = yf.download(
            tickers = stocks_watchlist,       # tickers list or string as well
            period = yf_period,      # optional, default is '1mo'
            interval = yf_interval,  # fetch data by intervaal
            group_by = 'ticker',     # group by ticker
            auto_adjust = True,      # adjust all OHLC (open-high-low-close)
            prepost = True,          # download market hours data
            threads = True,          # threads for mass downloading
            proxy = None) 

    #  2.  Select 'Close' (price at market close) column only
    yf_returns = yf_returns.iloc[:, yf_returns.columns.get_level_values(1)=='Close']


    #  3.  Remove the dataframe multi-index
    yf_returns.columns = yf_returns.columns.droplevel(1)

    yf_returns = round(yf_returns.pct_change()*100, 2)

    #  1. re-order columns
    col_order = []

    for i in stocks_watchlist:
        col_order.append(i)  # add tickers

    yf_returns = yf_returns[col_order] 

    perf_dy = yf_returns

    perf_dy['WEEK']  = perf_dy.index.strftime("%Y-%U")  # YEAR-WEEK


    #  create time dataframes using GROUPBY

    perf_wk = perf_dy.groupby('WEEK').sum()  # weekly performance


        
        #  plot #4
    plt.figure(figsize=(10,6))
    plt.plot(perf_wk[stocks_watchlist])
    plt.title('SYMBOLS', fontsize = 14)
    plt.ylabel('percent change', fontsize = 14)
    plt.legend(perf_wk[stocks_watchlist], loc="upper left", bbox_to_anchor=(1,1))
    plt.xticks(rotation = 90)
    plt.show()

    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url