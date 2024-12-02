from flask_sqlalchemy import SQLAlchemy
#what is sqlalchemy?
#  sqlachemy is a framework for creating and working with databases in Python and is a collection of tools and libraries that make it easier to work with databases in Python. it also provides a set of classes and functions that make it easier to work with databases in Python.
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, customer, professional
    is_active = db.Column(db.Boolean, default=True)  # True means user is active, False means restricted
 
class ProfessionalDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('base_service.id'), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    document_path = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')

    # Define relationships
    user = db.relationship('User', backref=db.backref('professional_details', lazy=True))
    service = db.relationship('BaseService', backref=db.backref('professionals', lazy=True))

class CustomerDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each customer
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Username/Email
    fullname = db.Column(db.String(100), nullable=False)  # Full Name
    address = db.Column(db.Text, nullable=False)  # Address of the customer
    pin_code = db.Column(db.String(10), nullable=False)  # PIN Code for location

class BaseService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Define relationship with Service model
    services = db.relationship('Service', backref='base_service', lazy=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_service_id = db.Column(db.Integer, db.ForeignKey('base_service.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_details.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location_pin_code = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # Relationships
    professional = db.relationship('ProfessionalDetails', backref=db.backref('services', lazy=True))

    @property
    def name(self):
        return self.base_service.name if self.base_service else None

    @property
    def description(self):
        return self.base_service.description if self.base_service else None

class ServiceBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_details.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional_details.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, declined, completed
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Define relationships
    customer = db.relationship('CustomerDetails', backref=db.backref('bookings', lazy=True))
    professional = db.relationship('ProfessionalDetails', backref=db.backref('bookings', lazy=True))
    service = db.relationship('Service', backref=db.backref('bookings', lazy=True))
