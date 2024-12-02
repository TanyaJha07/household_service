import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

# Create an instance of the Flask class
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///household_service.db"
app.config["UPLOAD_FOLDER"] = "uploads"  # Folder to save uploaded documents
app.secret_key = "your_secret_key"  # Needed for flash messages

from models import CustomerDetails, User, ProfessionalDetails, db, Service, ServiceBooking, BaseService

db.init_app(app)

with app.app_context():
    db.create_all()

# Ensure the upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def create_admin():
    admin = User(username="admin@gmail.com", password="admin123", role="admin")
    db.session.add(admin)
    db.session.commit()

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
        try:
            # Retrieve form data
            email = request.form.get("email")
            password = request.form.get("password")
            fullname = request.form.get("fullname")
            service_id = request.form.get("service_id")
            experience_years = request.form.get("experience_years")
            address = request.form.get("address")
            pin_code = request.form.get("pin_code")
            file = request.files["documents"]
            
            # Validate inputs
            if not all([email, password, fullname, service_id, experience_years, address, pin_code, file]):
                flash("All fields are required.", "danger")
                return redirect(url_for("signup_professional"))

            # Check if username already exists
            existing_user = User.query.filter_by(username=email).first()
            if existing_user:
                flash("Email already registered. Please use a different email or login.", "danger")
                return redirect(url_for("signup_professional"))

            # Verify if service exists
            service = BaseService.query.get(service_id)
            if not service:
                flash("Invalid service selected.", "danger")
                return redirect(url_for("signup_professional"))

            # Save the uploaded document
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
            else:
                flash("Document upload is required.", "danger")
                return redirect(url_for("signup_professional"))

            # Create a new user entry
            user = User(username=email, password=password, role="professional")
            db.session.add(user)
            db.session.flush()  # Get the user ID without committing

            # Create a new professional details entry
            professional = ProfessionalDetails(
                user_id=user.id,
                email=email,
                fullname=fullname,
                service_id=service_id,
                experience_years=int(experience_years),
                document_path=file_path,
                address=address,
                pin_code=pin_code
            )
            
            db.session.add(professional)
            db.session.commit()
            
            flash("Professional signup successful! Please wait for admin verification.", "success")
            return redirect(url_for("home"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("signup_professional"))

    # GET request - show available services
    services = BaseService.query.all()
    return render_template("signup_professional.html", services=services)

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
    
    # Get services from verified professionals
    services = Service.query.join(Service.professional).filter(
        ProfessionalDetails.status == 'verified'
    ).all()
    
    # Get recent bookings for the customer
    recent_bookings = ServiceBooking.query.filter_by(
        customer_id=customer.id
    ).order_by(
        ServiceBooking.created_at.desc()
    ).limit(5).all()
    
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
    # if "user_id" not in session or session["role"] != "admin":
    #     flash("Please login as admin to access this page.", "danger")
    #     return redirect(url_for("login"))
    
    # Get pending professional verifications
    pending_professionals = ProfessionalDetails.query.filter_by(status='pending').all()
    
    # Get all base services
    services = BaseService.query.order_by(BaseService.name).all()
    
    return render_template("admin_dashboard.html", 
                         pending_professionals=pending_professionals,
                         services=services)

@app.route("/all_users")
def all_users():
    if "user_id" not in session or session["role"] != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    # users = User.query.all()
    users = User.query.filter(User.role != 'admin').all()
    return render_template("all_users.html", users=users)
@app.route('/restrict_user/<int:user_id>', methods=['POST'])
def restrict_user_route(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    restrict_user(user_id)
    flash("User restricted successfully.", "success")
    return redirect(url_for('all_users'))

@app.route('/unrestrict_user/<int:user_id>', methods=['POST'])
def unrestrict_user_route(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))
    unrestrict_user(user_id)
    flash("User unrestricted successfully.", "success")
    return redirect(url_for('all_users'))

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

# Corrected search_services route
@app.route('/search_services')
def search_services():
    if not session.get('user_id'):
        flash('Please login to search services.', 'warning')
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()
    pin_code = request.args.get('pin_code', '').strip()

    # Base query
    services_query = Service.query

    # Apply search filters
    if query:
        services_query = services_query.filter(
            db.or_(
                Service.name.ilike(f'%{query}%'),
                Service.description.ilike(f'%{query}%')
            )
        )
    
    # Filter by PIN code if provided
    if pin_code:
        services_query = services_query.filter(BaseService.location_pin_code == pin_code)

    # Get verified professionals only
    services_query = services_query.join(ProfessionalDetails).filter(
        ProfessionalDetails.status == 'verified'
    )

    # Execute query and get results
    services = services_query.all()

    return render_template('search_results.html', services=services, query=query, pin_code=pin_code)

# Service Management Routes
@app.route("/add-service", methods=["POST"])
def add_service():
    if "user_id" not in session or session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    name = request.form.get("name")
    description = request.form.get("description")
    price = float(request.form.get("price"))
    
    try:
        service = BaseService(
            name=name,
            description=description,
            price=price
        )
        db.session.add(service)
        db.session.commit()
        flash("Service added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error adding service. Please try again.", "danger")
    
    return redirect(url_for("admin_dashboard"))

@app.route("/edit-service/<int:id>", methods=["POST"])
def edit_service(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    service = BaseService.query.get_or_404(id)
    
    try:
        service.name = request.form.get("name")
        service.description = request.form.get("description")
        service.price = float(request.form.get("price"))
        db.session.commit()
        flash("Service updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error updating service. Please try again.", "danger")
    
    return redirect(url_for("admin_dashboard"))

@app.route("/delete-service/<int:id>", methods=["POST"])
def delete_service(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    service = BaseService.query.get_or_404(id)
    
    try:
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting service. Please try again.", "danger")
    
    return redirect(url_for("admin_dashboard"))

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if  User.query.filter_by(username="admin@gmail.com").first() is None:
            create_admin()
    app.run(debug=True)
