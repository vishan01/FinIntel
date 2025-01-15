import yfinance as yf
from functools import lru_cache
from datetime import datetime
from flask_login import current_user
from src.models import db, User
import io
import base64
import matplotlib.pyplot as plt

def fetch_top_stocks():
    """Get data for top stocks."""
    top_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BRK-B', 'V', 'JNJ', 'WMT', 'JPM', 
                  'PG', 'UNH', 'NVDA', 'HD', 'DIS', 'PYPL', 'MA', 'VZ', 'ADBE', 'NFLX']
    stocks_data = []
    for ticker in top_stocks:
        stocks_data.append(fetch_stock_info(ticker))
    return stocks_data

def fetch_stock_info(ticker):
    """Get information for a specific stock."""
    stock_data = []
    ticker = ticker.upper().strip()
    stock = yf.Ticker(ticker)
    stock_info = stock.history(period='1d')
    if not stock_info.empty:
        row = stock_info.iloc[-1]
        price = row['Open']
        previous_close = stock_info.get('previousClose', row['Close'])
        change = price - previous_close
        stock_data = {
            'ticker': ticker,
            'price': round(row['Open'], 2),
            'high': round(row['High'], 2),
            'low': round(row['Low'], 2),
            'volume': round(row['Volume'], 2),
            'previous_close': round(previous_close, 2),
            'change': round(change, 2),
            'change_percent': round((change / previous_close) * 100 if previous_close else 0, 2),
            'date_time': row.name.strftime('%Y-%m-%d')
        }
    return stock_data

def plot_stocks(stocks_watchlist):
    """Generate performance plot for watchlist stocks."""
    yf_period = "1mo"
    yf_interval = "1d"
    yf_returns = yf.download(
        tickers=stocks_watchlist,
        period=yf_period,
        interval=yf_interval,
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )

    yf_returns = yf_returns.iloc[:, yf_returns.columns.get_level_values(1)=='Close']
    yf_returns.columns = yf_returns.columns.droplevel(1)
    yf_returns = round(yf_returns.pct_change()*100, 2)

    col_order = []
    for i in stocks_watchlist:
        col_order.append(i)

    yf_returns = yf_returns[col_order]
    perf_dy = yf_returns
    perf_dy['WEEK'] = perf_dy.index.strftime("%Y-%U")
    perf_wk = perf_dy.groupby('WEEK').sum()

    plt.figure(figsize=(10,6))
    plt.plot(perf_wk[stocks_watchlist])
    plt.title('SYMBOLS', fontsize=14)
    plt.ylabel('percent change', fontsize=14)
    plt.legend(perf_wk[stocks_watchlist], loc="upper left", bbox_to_anchor=(1,1))
    plt.xticks(rotation=90)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

class MarketDataService:
    def __init__(self):
        pass

    def get_market_indices(self):
        """Get current market indices data."""
        try:
            # Get sp 50 data using yfinance
            sp = yf.Ticker("^GSPC")  # sp 50 symbol
            info = sp.info
            price =info['open']
            previous_close = info.get('previousClose', price)
            change = price - previous_close
            data = {
                'sp': {
                    'price': price,
                    'change': change,
                    'change_percent': f"{(change / previous_close) * 100 if previous_close else 0:.2f}%",
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                }
            }
            
            # Add user's stock data if logged in
            if current_user.is_authenticated and current_user.stock_tickers:
                data['stocks'] = self.get_user_stocks()
            return data
        except Exception as e:
            return {'error': str(e)}

    def get_user_stocks(self):
        """Get stock data for user's watchlist."""
        if not current_user.stock_tickers:
            return []
            
        stocks_data = []
        tickers = current_user.stock_tickers.split(',')
        
        for ticker in tickers:
            ticker = ticker.strip()
            if not ticker:
                continue
                
            try:
                stock = yf.Ticker(ticker)
                history = stock.history(period='1d')
                if history.empty:
                    continue
                    
                row = history.iloc[-1]
                price = row['Close']
                previous_close = stock.info.get('previousClose', price)
                change = price - previous_close
                
                stocks_data.append({
                    'ticker': ticker,
                    'price': f"{price:.2f}",
                    'high': f"{row['High']:.2f}",
                    'low': f"{row['Low']:.2f}",
                    'volume': f"{row['Volume']:.2f}",
                    'previous_close': f"{previous_close:.2f}",
                    'change': f"{change:.2f}",
                    'change_percent': f"{(change / previous_close) * 100 if previous_close else 0:.2f}",
                    'date_time': row.name.strftime('%Y-%m-%d')
                })
            except Exception as e:
                print(f"Error fetching data for {ticker}: {str(e)}")
                continue
                
        return stocks_data

    def add_stock_to_watchlist(self, ticker):
        """Add a stock to user's watchlist."""
        if not current_user.is_authenticated:
            return False
            
        tickers = set(current_user.stock_tickers.split(',')) if current_user.stock_tickers else set()
        ticker = ticker.strip().upper()
        
        if ticker in tickers:
            return False
            
        tickers.add(ticker)
        current_user.stock_tickers = ','.join(filter(None, tickers))
        db.session.commit()
        return True

    def remove_stock_from_watchlist(self, ticker):
        """Remove a stock from user's watchlist."""
        if not current_user.is_authenticated:
            return False
            
        tickers = set(current_user.stock_tickers.split(',')) if current_user.stock_tickers else set()
        ticker = ticker.strip().upper()
        
        if ticker not in tickers:
            return False
            
        tickers.remove(ticker)
        current_user.stock_tickers = ','.join(filter(None, tickers))
        db.session.commit()
        return True

    def get_mutual_fund_nav(self, scheme_code):
        """Get mutual fund NAV data."""
        pass  # Implement if needed

    def get_fund_schemes(self):
        """Get list of mutual fund schemes."""
        pass  # Implement if needed
