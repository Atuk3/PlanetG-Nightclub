# Import necessary libraries
import json
import os
import io
import psycopg2
import datetime

from flask import Flask,render_template, request, jsonify,flash,url_for,redirect,session,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from flask_login import UserMixin,login_user,login_required,logout_user,current_user
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user,LoginManager


# Initialize Flask application
app=Flask(__name__)

# Set Flask application configurations
db=SQLAlchemy()
DB_NAME="database.db"
app.config['SECRET_KEY']='david'
app.config['UPLOAD_FOLDER']='static/files'
app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
db.init_app(app)

 



class User(db.Model,UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    service_year = db.Column(db.Integer, nullable=False)
    batch = db.Column(db.String(1), nullable=False)
    stream = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)


# Define Property model
class Property(db.Model):
    __tablename__ = 'properties'
    property_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    rent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    amenities = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=False)
    date=db.Column(db.DateTime(timezone=True), default=func.now())

# Define InspectionRequest model
# class InspectionRequest(db.Model):
#     __tablename__ = 'inspection_requests'


#     request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     property_id = db.Column(db.Integer, db.ForeignKey('properties.property_id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     request_datetime = db.Column(db.DateTime, nullable=False)

# # Define Review model
# class Review(db.Model):
#     __tablename__ = 'reviews'

#     review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     property_id = db.Column(db.Integer, db.ForeignKey('properties.property_id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     rating = db.Column(db.Integer, nullable=False)
#     comment = db.Column(db.Text, nullable=True)
#     date=db.Column(db.DateTime(timezone=True), default=func.now())


# # Define Favorite model
# class Favourite(db.Model):
#     __tablename__ = 'favourites'
#     favorite_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     property_id = db.Column(db.Integer, db.ForeignKey('properties.property_id'), nullable=False)



# Define the homepage route
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])

def home():

   # Render the homepage template for GET requests
    return render_template('index.html')




@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/services', methods=['GET', 'POST'])
def services():
    return render_template('services.html')


@app.route('/singleproperty', methods=['GET', 'POST'])   
def exclusive():
    return render_template('property-single.html')



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/privacy', methods=['GET', 'POST'])
def privacy():
    return render_template('privacy.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    return render_template('menu.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password is not None:  # Check if password is not None
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('User has no password set.', category='error')
        else:
            flash('Email does not exist.', category='error')
        
    

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
            first_name=request.form.get("first_name")
            last_name=request.form.get("last_name")
            email = request.form.get("email")
            phone_number = request.form.get("phonenumber")
            year = request.form.get("year")
            batch = request.form.get("batch")
            stream = request.form.get("stream")
            password = request.form.get("psw")
            confirm_psw = request.form.get("confirm_psw")
            account_type = request.form.get("account_type")
                
                #Validation
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists.', category='error')
           
            elif len(email) < 4:
                   flash('Email must be greater than 3 characters.') 
            elif not (email.endswith('@gmail.com') or email.endswith('@yahoo.com') or email.endswith('@outlook.com')):
                flash("Email must be either @gmail.com, @yahoo.com, or @outlook.com", "error")
                
 
            elif len(first_name) < 2:
                flash('First name must be greater than 1 character.', category='error')
            elif len(last_name) < 2:
                flash('Last name must be greater than 1 character.', category='error')
            elif len(phone_number) != 11 or not phone_number.isdigit():
                flash("Phone number must be 11 digits.", "error")
           
            current_year = datetime.datetime.now().year
            if int(year) < current_year - 1 or int(year) > current_year:
                flash(f"Service year must be between {current_year - 1} and {current_year}", "error")
                
            
            elif len(password) < 8:
                flash('Password must be at least 8 characters.', category='error')
            elif confirm_psw != password:
                 flash('Passwords don\'t match.', category='error')
            elif not account_type:
                flash("Please select an account type.", "error")
               
            elif not batch:
                flash("Please select a batch.", "error")
                
            elif not stream:
                flash("Please select a stream.", "error")

           
        # If no validation errors, proceed with account creation
        # Flash success message and redirect to login page  
            else:
                 
                new_user = User(email=email, first_name=first_name, last_name=last_name,phone_number=phone_number,service_year=year,batch=batch,stream=stream,account_type=account_type, password=generate_password_hash(
                    password, method='scrypt'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                return redirect(url_for('login'))
                
        
           
    return render_template('register.html',email=email, first_name=first_name, last_name=last_name,phone_number=phone_number,year=year,batch=batch,stream=stream, password=password,confirm_psw=confirm_psw)

@app.route('/recovery', methods=['GET', 'POST'])
def standard():
    return render_template('recovery.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/properties', methods=['GET', 'POST'])
def properties():
    return render_template('properties.html')

@app.route('/singleproperty', methods=['GET', 'POST'])
def singleproperty():
    return render_template('property-single.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password is not None:  # Check if password is not None
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('User has no password set.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template('test.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_property():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']
        filename = image.filename
        image.save(app.config['UPLOAD_FOLDER'] + '/' + filename)
        new_property = Property(name=name, description=description, image=filename, owner=current_user)
        db.session.add(new_property)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('upload.html')


with app.app_context():
    db.create_all()
    print('Created Database!')
# login_manager=LoginManager()
# login_manager.login_view='login'
# login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))

if __name__ == '__main__':
    app.run(debug=True)