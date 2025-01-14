import yfinance as yf
from functools import lru_cache
from datetime import datetime

class MarketDataService:
    def __init__(self, config):
        self.config = config

    @lru_cache(maxsize=1)
    def get_market_indices(self):
        """Get current market indices data."""
        try:
            # Get NIFTY 50 data using yfinance
            nifty = yf.Ticker("^NSEI")  # NIFTY 50 symbol
            info = nifty.info
            
            return {
                'nifty50': {
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChange', 0),
                    'change_percent': f"{info.get('regularMarketChangePercent', 0):.2f}%",
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                }
            }
        except Exception as e:
            return {'error': str(e)}

    def get_mutual_fund_nav(self, scheme_code):
        """Get mutual fund NAV data."""
        pass  # Implement if needed

    def get_fund_schemes(self):
        """Get list of mutual fund schemes."""
        pass  # Implement if needed
