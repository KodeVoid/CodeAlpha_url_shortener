# Flask application
from flask import Flask, render_template, request, jsonify, redirect
from app.connect_db import get_db_connection
import string
import random

app = Flask(__name__)

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/short', methods=['POST'])
def shorten():
    url = request.form.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if URL already exists
        cur.execute("SELECT id FROM urls WHERE long_url = %s;", (url,))
        existing = cur.fetchone()
        
        if existing:
            url_id = existing[0]
        else:
            # Insert the original URL
            cur.execute("INSERT INTO urls (long_url) VALUES (%s) RETURNING id;", (url,))
            url_id = cur.fetchone()[0]
        
        # Generate a unique shortcode with retry limit
        max_retries = 10
        for attempt in range(max_retries):
            code = generate_code()
            try:
                cur.execute("INSERT INTO shortcodes (url_id, code) VALUES (%s, %s);", (url_id, code))
                conn.commit()
                break
            except Exception as e:
                # Code already exists, try again
                if attempt == max_retries - 1:
                    return jsonify({"error": "Could not generate unique code"}), 500
                continue
        
        return jsonify({"short_url": f"http://localhost:5000/{code}"})
        
    except Exception as e:
        conn.rollback()
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