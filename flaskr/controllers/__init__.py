from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from flask_login import LoginManager
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from datetime import datetime, timedelta


db = SQLAlchemy()
DB_NAME = "database.db"
global ALLOWED_EXTENSIONS
ALLOWED_EXTENSIONS = {'xls', 'txt', 'csv'}

""" STORAGE FOR LOCAL TESTING """
# global UPLOAD_FOLDER
# UPLOAD_FOLDER = '../static/files'

# Function to load the .env configuration:
def load_env_config():
    load_dotenv()


def create_app():
    load_dotenv()
    app = Flask(__name__,static_folder='../static', template_folder='../templates')
    app.config['SECRET_KEY'] = getenv('SECRET_KEY') #Encrypts cookies and session data 
    """ DB FOR LOCAL TESTING """
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    """ DB FOR PRODUCTION """
    # app.config['SQLALCHEMY_DATABASE_URI'] = getenv('PSQL_URI')  

    """ AZURE BLOB STORAGE CONNECTION """
    global container_name, account_name, account_key, account_url
    storage_account_name = getenv('STORAGE_ACCOUNT_NAME')
    container_name = getenv('CONTAINER_NAME') # container name in which all experiment data will be stored
    account_key=getenv('ACCOUNT_KEY')
    account_url = getenv('ACCOUNT_URL')
    global blob_service_client
    sas_token = generate_account_sas(
                    account_name=storage_account_name,
                    account_key=account_key,
                    resource_types=ResourceTypes(service=True, container=True, object=True),
                    permission=AccountSasPermissions(read=True, write=True, list=True),
                    expiry=datetime.utcnow() + timedelta(hours=1))

    blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)
        
    
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

