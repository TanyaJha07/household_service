from flask import Flask, render_template


# Create an instance of the Flask class
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///household_service.db"

from models import User, db

db.init_app(app)

with app.app_context():
    db.create_all() 



















# Define a route for the home page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_professional")
def signup_professional():
    
    return render_template("signup_professional.html")
# Run the app
if __name__ == "__main__":
    app.run(debug=True)
