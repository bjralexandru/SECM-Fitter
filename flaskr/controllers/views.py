from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import  login_required, current_user
from werkzeug.utils import secure_filename
# from . import UPLOAD_FOLDER
from .cfit_secm import fit_data_Cornut
import pandas as pd
from .models import Data
from . import db
from sqlalchemy import select
from .id_generator import id_generator
import pandas as pd
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from . import blob_service_client
from datetime import datetime, timedelta
from os import getenv
from dotenv import load_dotenv


global container_name
global account
container_name = getenv('CONTAINER_NAME')
storage_account_name = getenv('STORAGE_ACCOUNT_NAME')

# The endpoints our users can access are stored here


views = Blueprint('views', __name__) # Blueprint for our Flask app 

@views.route('/', methods=['GET', 'POST']) # homepage
@login_required # makes sure you cannot access the home endpoint unless a user is logged in
def home():

    return render_template("home.html", user=current_user)  # user=current_user will render the page for that particular user


@views.route('/get_params', methods=['GET', 'POST'])
@login_required
def get_params():

    if request.method == 'GET':
        return render_template('get_params.html', user=current_user)
    #make them available to the database once the Kappa and Chi2 are
    # finally calculated.
    
    if request.method == 'POST':
        global rT, RG, K, iTinf, title 

        file = request.files
        rT = request.form.get('rT')
        iTinf = request.form.get('iTinf')
        RG = request.form.get('RG')
        K = request.form.get('K')
        title = request.form.get('title')
        #TODO: implement function fit_data(path/tofile, rT, iTinf, RG, K)
        

        # Cast inputs to float type
        # ALSO
        # Check that the values are in the correct interval

        try:
            rT = float(rT)
            # if rT < 0:
            #     flash("Electrode radius cannot be a negative number!", category='error')
        except ValueError:
            flash("Please input a valid number!", category='error')
        try:
            iTinf = float(iTinf)
            # if iTinf < -1000 or iTinf > 1000:
            #     flash("Current value too large! (min: -1000nA, max: +1000nA)", category='error')
        except ValueError:
            flash("Please input a valid number!", category='error')
        try:
            RG = float(RG)
            # if RG < 3 or RG > 15:
            #     flash("The fitting function provides correct answers for RG values bettwen 3 and 15.", category='error')
        except ValueError:
            flash("Please input a valid number!", category='error')
        try:
            K = float(K)
            # if K < 0 or K > 3:
            #     flash("K values cannot exceed 3.", category='error')
        except ValueError:
            flash("Please input a valid number!", category='error')

        """ OLD WAY OF PROCESSING FILE UPLOAD LOCALLY"""
         # Process the file upload 
        # try:
        #     file = request.files['file']
        #     if file and allowed_file(file.filename):
        #         """ For local testing """
        #         #file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), UPLOAD_FOLDER, secure_filename(file.filename)))

        """ NEW WAY OF STORING FILES IN THE CLOUD """      
        global filename
        file = request.files['file']
        filename = secure_filename(file.filename)
        # Extract extensions and modify the initial upload's name to a random string
        fileextension = filename.rsplit('.',1)[1]
        Randomfilename = id_generator()
        filename = Randomfilename + '.' + fileextension
        # Establish connection to the remote blob on Azure Portal and upload the file
        try:
            global blob_client
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
            blob_client.upload_blob(file)
        except Exception as e:
            print(e) 
            pass

        # This link is used to access the file having a random name, but the user afterwards selects his own title.
        user_upload_path =  'http://'+ storage_account_name + '.blob.core.windows.net/' + container_name + '/' + filename
        
        """ Here we do the fitting of the remote data """
        global processed_dataset
        processed_dataset = title + '.csv' # Save it as a .csv TODO: make it a variable
        global processed_params
        processed_params = title + '_params' + '.csv' #TODO: make it a variable

        # Dumb, I know but something in my folder structure wont let me export the variables as they are.

        try:
            # These should be 2 csv files one with the extracted params and one with the final dataset
                # and they will be later stored alongside the original user's upload for storage and later query.
            fit_params_output = fit_data_Cornut(user_upload_path,float(rT), float(RG), float(iTinf), float(K))[0].to_csv(index='false', encoding='utf-8')
            fit_dataset_output = fit_data_Cornut(user_upload_path,float(rT), float(RG), float(iTinf), float(K))[1].to_csv(index='false', encoding='utf-8')
            
            try:
                # TODO: Problems may arise when people try to save file under the same name
                blob_client.upload_blob(fit_dataset_output)
                blob_client.upload_blob(fit_params_output)
            except Exception as e:
                print(e)
                pass
            return redirect(url_for("views.fit_data"))
        except ValueError:
            flash("Please input a valid values for rT, iTinf, RG and Kappa!", category='error')
        return render_template("get_params.html", user=current_user)

@views.route('/fit_data', methods=['GET', 'POST'])
@login_required
def fit_data():
    if request.method == 'POST':
        return redirect(url_for("views.deliver_graph_content"))
    return render_template("fit_data.html", user=current_user)

@views.route('/results', methods=['GET','POST'])
# Tried to build a new endpoint which renders the picture inside the canvas div. 
@login_required
def deliver_graph_content():
    # First we construct a dataframe with the processed data: 1 for the graph & 1 for the parameters of interest
    global url_for_dataset_processed
    global url_for_params_processed
    url_for_dataset_processed = 'http://'+ storage_account_name + '.blob.core.windows.net/' + container_name + '/' + processed_dataset
    url_for_params_processed = 'http://'+ account + '.blob.core.windows.net/' + container_name + '/' + processed_params
    data_to_represent = pd.read_csv(url_for_dataset_processed)
    params = pd.read_csv(url_for_params_processed)

    # Get the distance and currents arrays in separate variables and deliver them to Chart.js inside the 'result.html'
    # to be rendered. 

    distance_values = data_to_represent['L_data'].tolist()
    experiment_current_values = data_to_represent['iT_experimental'].tolist()
    theoretical_current_values = data_to_represent['iT_simulated'].tolist()
    Kappa = params['Kappa'].tolist()[0]
    Chi2 = params['Chi2'].tolist()[0]
    new_Data = Data(title=title, rT=rT, RG=RG, iT_inf=iTinf, Kappa=Kappa, Chi2=Chi2, user_id=current_user.id)
    db.session.add(new_Data)
    db.session.commit()
    return render_template('results.html', user=current_user, labels=distance_values, values1=experiment_current_values, values2=theoretical_current_values, Kappa=Kappa, Chi2=Chi2)


''' QUERY DATA ENDPOINTS '''

@views.route('/query_data', methods=['GET', 'POST'])
@login_required
def query_data():

    if request.method == 'GET':
        #TODO: Get the experiment title displayed in a drop-down list 
        archived_experiment = db.session.execute(select(Data.title).where(Data.user_id == current_user.id).order_by(Data.date))
        dropdown_list_items = []  # We iterate over this array to dinamically generate the html rendered dropdown list.
        for row in archived_experiment:
            dropdown_list_items.append(row[0]) 
        return render_template('query_data.html', user=current_user, dropdown_list_items=dropdown_list_items)
    if request.method == 'POST':
        
        return redirect(url_for('views.query_results'))


@views.route('/query_results', methods=['GET', 'POST'])
@login_required
def query_results():
        search_title = request.form.get('archived_experiments')
        global data_to_represent, params
        #TODO: catch error in case someone doesnt choose a value from the dropdown. 
        data_to_represent = pd.read_csv(url_for_dataset_processed)
        params = pd.read_csv(url_for_params_processed)
    # Get the distance and currents arrays in separate variables and deliver them to Chart.js inside the 'result.html'
        # to be rendered. 
        global distance_values, experiment_current_values, theoretical_current_values, Kappa, Chi2
        distance_values = data_to_represent['L_data'].tolist()
        experiment_current_values = data_to_represent['iT_experimental'].tolist()
        theoretical_current_values = data_to_represent['iT_simulated'].tolist()
        Kappa = params['Kappa'].tolist()[0]
        Chi2 = params['Chi2'].tolist()[0]
        return render_template('query_results.html', user=current_user, labels=distance_values, values1=experiment_current_values, values2=theoretical_current_values, Kappa=Kappa, Chi2=Chi2)

@views.route('/How-It-Works', methods=['GET'])
@login_required
def howitworks():
    return render_template('howitworks.html', user=current_user)