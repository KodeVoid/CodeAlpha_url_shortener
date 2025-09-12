# Flask application
from flask import Flask, render_template, request, jsonify, redirect
from app.connect_db import get_db_connection
import string
from dotenv import load_dotenv
import random
import os
import sys

app = Flask(__name__)
load_dotenv()

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

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/short', methods=['POST'])
def shorten():
    url = request.json.get("url") if request.is_json else request.form.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Find or insert long URL
        cur.execute("SELECT id FROM urls WHERE long_url = %s;", (url,))
        row = cur.fetchone()
        if row:
            url_id = row[0]
        else:
            cur.execute("INSERT INTO urls (long_url) VALUES (%s) RETURNING id;", (url,))
            url_id = cur.fetchone()[0]
            conn.commit()

        # Check for existing shortcode
        cur.execute("SELECT code FROM shortcodes WHERE url_id = %s;", (url_id,))
        row = cur.fetchone()
        if row:
            code = row[0]
        else:
            # Try to insert new shortcode with retries
            for attempt in range(10):
                code = generate_code()
                try:
                    cur.execute("INSERT INTO shortcodes (url_id, code) VALUES (%s, %s);", (url_id, code))
                    conn.commit()
                    break
                except Exception as e:
                    conn.rollback()
                    if attempt == 9:
                        app.logger.error(f"Failed to insert shortcode: {e}")
                        return jsonify({"error": "Could not generate unique code"}), 500
                    continue

        return jsonify({"short_url": f"{base_url}/{code}"})

    except Exception as e:
        conn.rollback()
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/<short>')
def map_url(short):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT u.long_url
            FROM shortcodes s
            JOIN urls u ON s.url_id = u.id
            WHERE s.code = %s;
        """, (short,))
        
        row = cur.fetchone()
        
        if row:
            original_url = row[0]
            # Add protocol if missing
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'http://' + original_url
            return redirect(original_url)
        else:
            return jsonify({"error": "Shortcode not found"}), 404
            
    except Exception as e:
        return jsonify({"error": "Database error"}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    # Uncomment to set up database on first run
    # setup_database()
    app.run(debug=True)