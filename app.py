from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from utils.db import init_db
from routes.auth import auth_bp
from routes.expense import expense_bp
from routes.category import category_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    
    return app