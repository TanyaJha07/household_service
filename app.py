from flask import Flask, render_template


# Create an instance of the Flask class
app = Flask(__name__)

# Define a route for the home page
@app.route("/")
def home():
    return render_template("index.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)