from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from src.models import db, User
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///finintel.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
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
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(finance_bp, url_prefix='/finance')  # Changed from '/api/finance'

    @app.route('/')
    def home():
        return render_template('home.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
