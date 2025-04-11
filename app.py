from flask import Flask, render_template
from flask_cors import CORS
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from admin.routes import admin_bp
from db import initialize_database

app = Flask(__name__)
CORS(app)
app.secret_key = "secret_key"
initialize_database()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
