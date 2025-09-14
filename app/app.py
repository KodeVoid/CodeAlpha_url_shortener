# Flask application
from flask import Flask, render_template, request, jsonify, redirect
from app.connect_db import get_db_connection
import string
from dotenv import load_dotenv
from flask_cors import CORS 
import random
import os
import sys
from app.errors import register_error_handlers
from app.routes import Routes

app = Flask(__name__)
load_dotenv()
CORS(app, origins=['http://localhost:8080'])  # Only allow Swagger Editor

# Abort program if BASE_URL is not set
try:
    base_url = os.environ["BASE_URL"]
    if not base_url.strip():  # Check if empty or whitespace only
        raise ValueError("BASE_URL cannot be empty")
except KeyError:
    print("❌ ERROR: BASE_URL environment variable is required!")
    print("📝 Please set BASE_URL in your environment")
    sys.exit(1)
except ValueError as e:
    print(f"❌ ERROR: {e}")
    print("📝 Please set a valid BASE_URL in your environment")
    sys.exit(1)

print(f"✅ Using BASE_URL: {base_url}")

# Register global error handlers
register_error_handlers(app)

# Initialize routes - this will automatically register all routes
routes = Routes(app)

# Add a simple home route if you want to keep the template rendering
@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)