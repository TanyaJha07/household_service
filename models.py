from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
