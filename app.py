import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

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

        # Create a new user entry
        user = User(username=email, password=password, role="customer")
        db.session.add(user)
        db.session.commit()
        user=User.query.filter_by(username=email).first()
        
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
        print("name")
        print(email, password, fullname, service_name, experience_years, address, pin_code, file)
        # Validate inputs
        if not all([email, password, fullname, service_name, experience_years, address, pin_code, file]):
            flash("All fields are required.", "danger")
            return redirect(url_for("signup_professional"))
        print("hi")
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
        )
        db.session.add(professional)
        db.session.commit()

        flash("Professional signup successful! Please wait for admin verification.", "success")
        return redirect(url_for("home"))

    return render_template("signup_professional.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
