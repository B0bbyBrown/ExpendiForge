from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from models import db, User, Category
from config import Config
import os

def seed_categories():
    initial_categories = [
        'Office Supplies',
        'Electronics',
        'Services',
        'Miscellaneous'
    ]
    
    for cat_name in initial_categories:
        if not Category.query.filter_by(name=cat_name).first():
            category = Category(name=cat_name, description='')
            db.session.add(category)
    
    db.session.commit()

def seed_dev_users():
    dev_users = [
        {
            'username': 'shopper',
            'email': 'shopper@dev.com',
            'password': 'shopper123',
            'role': 'shopper'
        },
        {
            'username': 'admin',
            'email': 'admin@dev.com',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'username': 'dev',
            'email': 'dev@dev.com',
            'password': 'dev123',
            'role': 'dev'
        }
    ]
    
    for user_data in dev_users:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
    
    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
        seed_categories()
        seed_dev_users()
    
    from routes import register_routes
    register_routes(app)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app
