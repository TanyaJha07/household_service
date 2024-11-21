from flask_sqlalchemy import SQLAlchemy
#what is sqlalchemy?
#  sqlachemy is a framework for creating and working with databases in Python and is a collection of tools and libraries that make it easier to work with databases in Python. it also provides a set of classes and functions that make it easier to work with databases in Python.
db = SQLAlchemy()
# db is a variable that stores an instance of the SQLAlchemy class, which is a framework for creating and working with databases in Python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, customer, professional

class ProfessionalDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each professional
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Username/Email
    fullname = db.Column(db.String(100), nullable=False)  # Full Name
    service_name = db.Column(db.String(100), nullable=False)  # Name of the Service
    experience_years = db.Column(db.Integer, nullable=False)  # Experience in years
    document_path = db.Column(db.String(200), nullable=False)  # Path to uploaded document
    address = db.Column(db.Text, nullable=False)  # Address of the professional
    pin_code = db.Column(db.String(10), nullable=False)  # PIN Code for location
    is_verified = db.Column(db.Boolean, default=False)  # Indicates if admin verified the professional

class CustomerDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each customer
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Username/Email
    fullname = db.Column(db.String(100), nullable=False)  # Full Name
    address = db.Column(db.Text, nullable=False)  # Address of the customer
    pin_code = db.Column(db.String(10), nullable=False)  # PIN Code for location
