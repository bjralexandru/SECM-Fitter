from crypt import methods
import os
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import  login_required, current_user
from werkzeug.utils import secure_filename
from . import UPLOAD_FOLDER
from .import allowed_file
from .cfit_secm import fit_data_Cornut, save_file, display_graph
import pandas as pd
import json
from .models import User, Data
from . import db
from sqlalchemy import select


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

         # Process the file upload 
        try:
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), UPLOAD_FOLDER, secure_filename(file.filename)))
                flash("File uploaded successfully!", category="success")
            else:
                flash('File format not supported! Please follow guide on how to setup the .xls file at /home/guide.', category='error')
        except FileNotFoundError:
                flash("No file selected. Plase provide a file to process!", category='error')
        
        global path # make it accessible to fitdata function below
        
        # Get the name of the file provided by the user without the extension 
        # for further use.
        filename = str(file.filename)
        first_file_part = filename.split('.')
        final_name = first_file_part[0].split('/')
        path = '../static/files/'+final_name[0]
        global figure
        figure = str('../static/files/'+final_name[0]+'.png')
        # If everything works fine, call the fitting function with the file path as param + '.xls' 
        # because the fitting script only takes the original dataset in .xls format.
        try:
            fit_data_Cornut(path+'.xls',float(rT), float(RG), float(iTinf), float(K))
            # We then store the processed data in a separate file which is saved alongside the original dataset
            save_file('../static/files/'+title)
            return redirect(url_for("views.fit_data"))
        except ValueError:
            flash("Please input a valid values for rT, iTinf, RG and Kappa!", category='error')
        except FileNotFoundError:
            flash("No file selected. Plase provide a file to process!", category='error')
        return render_template("get_params.html", user=current_user)

@views.route('/fit_data', methods=['GET', 'POST'])
@login_required
def fit_data():
    if request.method == 'POST':
        display_graph('../static/files/'+title) #TODO: Delete this functionality. Not useful anymore.
        return redirect(url_for("views.deliver_graph_content"))
    return render_template("fit_data.html", user=current_user)

@views.route('/results', methods=['GET','POST'])
# Tried to build a new endpoint which renders the picture inside the canvas div. 
@login_required
def deliver_graph_content():
    # First we construct a dataframe with the processed data: 1 for the graph & 1 for the parameters of interest
    data_to_represent = pd.read_csv('../static/files/'+title+'_processed.csv')
    params = pd.read_csv('../static/files/'+title+'_params'+'.csv')

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
        data_to_represent = pd.read_csv('../static/files/'+search_title+'_processed.csv')
        params = pd.read_csv('../static/files/'+search_title+'_params'+'.csv')
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