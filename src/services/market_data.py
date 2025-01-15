import yfinance as yf
from functools import lru_cache
from datetime import datetime
from flask_login import current_user
from src.models import db, User

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
