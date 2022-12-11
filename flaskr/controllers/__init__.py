from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from flask_login import LoginManager
from dotenv import load_dotenv

global UPLOAD_FOLDER
global ALLOWED_EXTENSIONS

db = SQLAlchemy()
DB_NAME = "database.db"
ALLOWED_EXTENSIONS = {'xls', 'txt', 'csv'}
UPLOAD_FOLDER = '../static/files'


# Function to load the .env configuration:
def load_env_config():
    load_dotenv()

def create_app():
    load_dotenv()
    app = Flask(__name__,static_folder='../static', template_folder='../templates')
    app.config['SECRET_KEY'] = getenv('SECRET_KEY') #Encrypts cookies and session data 
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MHwdnEVDKeNfH3uP7PnE@containers-us-west-164.railway.app:5455/railway'  

    
    
    db.init_app(app)



    # import views 
    from .views import views 
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models

    create_database(app)


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # Where should Flask redirect an user by default if he is not logged in
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id)) # Tell Flask what user are we looking for when signing in.
    
    return app

def create_database(app):
    if not path.exists('website/'+ DB_NAME):
        with app.app_context():
            db.create_all()
        print('Database created!')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

