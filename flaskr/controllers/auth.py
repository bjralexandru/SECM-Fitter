from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.controllers.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user


# The endpoints our users can access are stored here


auth = Blueprint('auth', __name__) 

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first() #filter all users and find the email
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) #login the user and store the session until the server crashes or the user logsout from their browser
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password, try again.", category='error')
        else:
            flash("Incorrect email!", category='error')

    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required # makes sure you cannot acces this route unless some1 is logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():

    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first() # Make sure you dont sign-up a person twice
        
        if user:
            flash('Email already exists!', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Passwords must be at least 8 characters in length.', category='error')
        else: 
            # TODO: add user to db
            new_user = User(email=email, first_name=firstName, last_name=lastName, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True) #login the user and store the session until the server crashes or the user logsout from their browser
            flash("Success! Your account has been created!", category="success")
            return redirect(url_for('views.home'))
    return render_template('sign_up.html', user=current_user)