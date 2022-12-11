from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from flask_login import LoginManager
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# global UPLOAD_FOLDER
global ALLOWED_EXTENSIONS

db = SQLAlchemy()
DB_NAME = "database.db"
ALLOWED_EXTENSIONS = {'xls', 'txt', 'csv'}

""" STORAGE FOR LOCAL TESTING """
# UPLOAD_FOLDER = '../static/files'

# Function to load the .env configuration:
def load_env_config():
    load_dotenv()


def create_app():
    load_dotenv()
    app = Flask(__name__,static_folder='../static', template_folder='../templates')
    app.config['SECRET_KEY'] = getenv('SECRET_KEY') #Encrypts cookies and session data 
    """ DB FOR LOCAL TESTING """
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    """ DB FOR PRODUCTION """
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('PSQL_URI')  

    """ AZURE BLOB STORAGE CONNECTION """
    global container_name, account
    account = getenv('ACCOUNT_NAME')
    connect_str = getenv('AZURE_STORAGE_CONNECTION_STRING') # retrieve secret connection string from env variables
    container_name = "fitting" # container name in which all experiment data will be stored


    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # Instance of the Blob Client that established the transfer of data
    global container_client

    try:     
        container_client = blob_service_client.get_container_client(container=container_name) # Glue togheter the container declared locally to the remote one
        container_client.get_container_properties() # This will throw an error, which we can catch, in case that the remote container doesn't exist 
    except Exception as e:
        print(e)
        print(f"Container doesn't exist. Creating your new \'{container_name}\' container ...")
        container_client = blob_service_client.create_container(container_name)

    
    
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

