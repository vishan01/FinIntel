from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from src.models import db, User
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finintel.db')
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        self.ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

def create_app():
    app = Flask(__name__)
    config = Config()
    
    # Configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.finance import finance_bp
    
    # Initialize services with config
    from src.services.financial import FinancialService
    from src.services.market_data import MarketDataService
    
    financial_service = FinancialService(config)
    market_service = MarketDataService()
    
    # Pass services to blueprints
    from src.routes.finance import init_services
    init_services(financial_service, market_service)
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(finance_bp, url_prefix='/finance')

    @app.route('/')
    def home():
        return render_template('home.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
