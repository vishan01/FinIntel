# FinIntel Project Knowledge

## Project Setup
- Flask 3.0.0 based REST API with SQLAlchemy ORM
- Uses python-dotenv for environment management
- Development server runs in debug mode
- Uses Gemini AI for financial insights and learning
- SQLite database for development (configurable for production)

## Project Structure
- `app.py`: Main application entry point
- `src/models/`: Database models
- `src/routes/`: API routes and views
- `src/services/`: Business logic and external services
- `src/utils/`: Helper functions and utilities
- `.env`: Environment configuration
- `requirements.txt`: Python dependencies

## Development Guidelines
- Use SQLAlchemy 2.0 style: prefer db.session.get() over Query.get()
- Use virtual environment (venv) for development
- Install dependencies with `pip install -r requirements.txt`
- Run server with `flask run` or `python app.py`
- Always add new dependencies to requirements.txt
- Keep sensitive information in .env file
- Use blueprints for route organization
- Follow PEP 8 style guidelines

## Database Models
- User: Core user model with authentication
- Expense: Tracks user expenses with categories
- Budget: Monthly budget limits by category
- Goal: Financial goals with target amounts and dates

## Security Notes
- Never commit .env file
- Use environment variables for sensitive data
- Hash passwords before storing
- Use Flask-Login for session management

## External Integrations
- Alpha Vantage API for real-time stock market data (free tier: 5 API calls per minute, 500 per day)
- AMFI API for mutual fund data (free, no key required)
- Cache market data responses using lru_cache
- Use async calls for external APIs
- Rate limiting required for Alpha Vantage API

## API Keys Required
- Alpha Vantage API key from https://www.alphavantage.co/support/#api-key (free tier: 5 API calls per minute, 500 per day)
- Google API key for Gemini AI

## Data Serialization
- Always convert Decimal/numeric types to float before JSON serialization
- Sort time-series data chronologically before sending to frontend
- Handle empty dataset cases explicitly

## Market Data Integration
- Uses Yahoo Finance (yfinance) for real-time market data
- Cache responses using lru_cache to optimize performance
- Currently displays NIFTY 50 index on home page
- Error handling and loading states implemented
- No API key required for basic usage

## AI Integration
- Uses Gemini AI for financial advice and chat
- Interactive chat interface in advice page
- Supports both structured topics and free-form questions

