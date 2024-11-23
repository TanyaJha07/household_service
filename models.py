from flask_sqlalchemy import SQLAlchemy
#what is sqlalchemy?
#  sqlachemy is a framework for creating and working with databases in Python and is a collection of tools and libraries that make it easier to work with databases in Python. it also provides a set of classes and functions that make it easier to work with databases in Python.
db = SQLAlchemy()

class User(db.Model):
    # model is a class that represents a table in the database and is used to define the structure of the table
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
    status = db.Column(db.String(20), nullable=False, default='pending')  # Status can be: pending, verified, rejected

class CustomerDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each customer
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Username/Email
    fullname = db.Column(db.String(100), nullable=False)  # Full Name
    address = db.Column(db.Text, nullable=False)  # Address of the customer
    pin_code = db.Column(db.String(10), nullable=False)  # PIN Code for location

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_details.id'), nullable=False)
    location_pin_code = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    professional = db.relationship('ProfessionalDetails', backref=db.backref('services', lazy=True))

class ServiceBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_details.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_details.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, declined, completed
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # Relationships
    customer = db.relationship('CustomerDetails', backref=db.backref('bookings', lazy=True))
    professional = db.relationship('ProfessionalDetails', backref=db.backref('bookings', lazy=True))
