import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

# Create an instance of the Flask class
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///household_service.db"
app.config["UPLOAD_FOLDER"] = "uploads"  # Folder to save uploaded documents
app.secret_key = "your_secret_key"  # Needed for flash messages

from models import CustomerDetails, User, ProfessionalDetails, db

db.init_app(app)

with app.app_context():
    db.create_all()

# Ensure the upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Define a route for professional signup
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        
        # Retrieve form data
        email = request.form.get("email")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        address = request.form.get("address")
        pin_code = request.form.get("pincode")
        
        # Validate inputs
        if not all([email, password]):
            flash("All fields are required.", "danger")
            return redirect(url_for("signup"))

        # Check if username already exists
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "danger")
            return redirect(url_for("signup"))

        try:
            # Create a new user entry
            user = User(username=email, password=password, role="customer")
            db.session.add(user)
            db.session.commit()

            # Create a new customer details entry
            customer = CustomerDetails(
                user_id=user.id,
                email=email,
                fullname=fullname,
                address=address,
                pin_code=pin_code,
            )
            
            db.session.add(customer)
            db.session.commit()
            
            flash("Signup successful! Please wait for admin verification.", "success")
            return redirect(url_for("home"))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for("signup"))
    return render_template("signup.html")

@app.route("/signup_professional", methods=["GET", "POST"])
def signup_professional():
    if request.method == "POST":
        
        # Retrieve form data
        email = request.form.get("email")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        service_name = request.form.get("service_name")
        experience_years = request.form.get("experience_years")
        address = request.form.get("address")
        pin_code = request.form.get("pin_code")
        file = request.files["documents"]
        
        # Validate inputs
        if not all([email, password, fullname, service_name, experience_years, address, pin_code, file]):
            flash("All fields are required.", "danger")
            return redirect(url_for("signup_professional"))

        # Check if username already exists
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "danger")
            return redirect(url_for("signup_professional"))

        try:
            # Save the uploaded document
            if file and file.filename.endswith(".pdf"):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
            else:
                flash("Please upload a valid PDF document.", "danger")
                return redirect(url_for("signup_professional"))

            # Create a new user entry
            user = User(username=email, password=password, role="professional")
            db.session.add(user)
            db.session.commit()

            # Create a new professional details entry
            professional = ProfessionalDetails(
                user_id=user.id,
                email=email,
                fullname=fullname,
                service_name=service_name,
                experience_years=int(experience_years),
                document_path=file_path,
                address=address,
                pin_code=pin_code,
                status='pending'
            )
            db.session.add(professional)
            db.session.commit()

            flash("Professional signup successful! Please wait for admin verification.", "success")
            return redirect(url_for("home"))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for("signup_professional"))

    return render_template("signup_professional.html")

def create_admin():
    admin = User(username="admin@gmail.com", password="admin123", role="admin")
    db.session.add(admin)
    db.session.commit()

# Define a route for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Validate inputs
        if not all([email, password]):
            flash("Please enter both email and password.", "danger")
            return redirect(url_for("login"))
        
        # Check if user exists and password is correct
        user = User.query.filter_by(username=email).first()
        if user and user.password == password:  # In production, use proper password hashing
            session["user_id"] = user.id
            session["role"] = user.role
            flash("Login successful!", "success")
            
            # Redirect based on user role
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "professional":
                return redirect(url_for("professional_dashboard"))
            else:  # customer
                return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))
    
    return render_template("login.html")

# Dashboard routes with role-based access control
@app.route("/user-dashboard")
def user_dashboard():
    if "user_id" not in session or session["role"] != "customer":
        flash("Please login as a customer to access this page.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    customer = CustomerDetails.query.filter_by(user_id=user_id).first()
    
    # Get all verified professionals for available services
    services = ProfessionalDetails.query.filter_by(status='verified').all()
    
    # In a real application, you would fetch these from your database
    recent_bookings = []  # You'll need to implement this based on your booking model
    
    return render_template("user_dashboard.html", 
                         customer=customer, 
                         services=services,
                         recent_bookings=recent_bookings)

@app.route("/professional-dashboard")
def professional_dashboard():
    if "user_id" not in session or session["role"] != "professional":
        flash("Please login as a professional to access this page.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    professional = ProfessionalDetails.query.filter_by(user_id=user_id).first()
    
    # In a real application, you would fetch these from your database
    service_requests = []  # You'll need to implement this based on your booking model
    stats = {
        "pending": 0,
        "completed": 0,
        "total": 0
    }
    
    return render_template("professional_dashboard.html", 
                         professional=professional,
                         service_requests=service_requests,
                         stats=stats)

@app.route("/admin-dashboard")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        flash("Please login as an admin to access this page.", "danger")
        return redirect(url_for("login"))
    professionals = ProfessionalDetails.query.filter_by(status='pending').all()
    return render_template("admin_dashboard.html", pending_professionals=professionals)

@app.route("/verify-professional/<int:id>", methods=["POST"])
def verify_professional(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    professional = ProfessionalDetails.query.get_or_404(id)
    professional.status = 'verified'
    db.session.commit()
    flash(f"Professional {professional.fullname} has been verified.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/reject-professional/<int:id>", methods=["POST"])
def reject_professional(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    professional = ProfessionalDetails.query.get_or_404(id)
    professional.status = 'rejected'
    db.session.commit()
    flash(f"Professional application has been rejected.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/update-profile", methods=["POST"])
def update_profile():
    if "user_id" not in session or session["role"] != "customer":
        flash("Please login to update your profile.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    customer = CustomerDetails.query.filter_by(user_id=user_id).first()
    
    if customer:
        customer.fullname = request.form.get("fullname")
        customer.address = request.form.get("address")
        customer.pin_code = request.form.get("pin_code")
        db.session.commit()
        flash("Profile updated successfully!", "success")
    else:
        flash("Customer profile not found.", "danger")
    
    return redirect(url_for("user_dashboard"))

@app.route("/update-professional-profile", methods=["POST"])
def update_professional_profile():
    if "user_id" not in session or session["role"] != "professional":
        flash("Please login to update your profile.", "danger")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    professional = ProfessionalDetails.query.filter_by(user_id=user_id).first()
    
    if professional:
        professional.fullname = request.form.get("fullname")
        professional.service_name = request.form.get("service_name")
        professional.experience_years = request.form.get("experience_years")
        professional.address = request.form.get("address")
        professional.pin_code = request.form.get("pin_code")
        db.session.commit()
        flash("Profile updated successfully!", "success")
    else:
        flash("Professional profile not found.", "danger")
    
    return redirect(url_for("professional_dashboard"))

@app.route("/book-service/<int:service_id>", methods=["POST"])
def book_service(service_id):
    if "user_id" not in session or session["role"] != "customer":
        flash("Please login to book a service.", "danger")
        return redirect(url_for("login"))
    
    professional = ProfessionalDetails.query.get_or_404(service_id)
    customer = CustomerDetails.query.filter_by(user_id=session["user_id"]).first()
    
    if not professional.status == 'verified':
        flash("This professional is not yet verified.", "danger")
        return redirect(url_for("user_dashboard"))
    
    # Here you would typically create a booking record in your database
    # For now, we'll just show a success message
    flash("Service booked successfully!", "success")
    return redirect(url_for("user_dashboard"))

@app.route("/accept-request/<int:request_id>", methods=["POST"])
def accept_request(request_id):
    if "user_id" not in session or session["role"] != "professional":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    # Here you would typically update the request status in your database
    flash("Request accepted successfully!", "success")
    return redirect(url_for("professional_dashboard"))

@app.route("/decline-request/<int:request_id>", methods=["POST"])
def decline_request(request_id):
    if "user_id" not in session or session["role"] != "professional":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    # Here you would typically update the request status in your database
    flash("Request declined.", "success")
    return redirect(url_for("professional_dashboard"))

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if  User.query.filter_by(username="admin@gmail.com").first() is None:
            create_admin()
    app.run(debug=True)
