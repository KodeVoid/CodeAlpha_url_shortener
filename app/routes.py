import os
from flask import request, jsonify, redirect
from app.connect_db import get_db_connection
import string
import random

class Routes(object):
    """A class to manage routes for the app"""
    
    def __init__(self, app):  # Fixed: __init__ instead of **init**
        self.app = app
        self.base_url = os.environ.get("BASE_URL")
        self.register_routes()  # Call register_routes during initialization
    
    def register_routes(self):  # Fixed: Added self parameter
        # Fixed: Correct syntax for route registration
        self.app.route('/v1/urls', methods=['GET'])(self.get_urls)
        self.app.route('/v1/urls', methods=['POST'])(self.create_short_url)
        self.app.route('/v1/urls/<id>', methods=['GET'])(self.get_url)  # Fixed: Added missing /
        self.app.route('/<id>/redirect', methods=['GET'])(self.redirect_to_original_url)  # Fixed: Better route pattern
    
    def generate_code(self, length=6):
        """Generate a random short code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def get_urls(self):  # Fixed: Added self parameter
        """GET /v1/urls - Get paginated list of URLs"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)
            
            # Validate pagination parameters
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 10
                
            offset = (page - 1) * limit
            
            # Get total count for pagination
            cur.execute("""
                SELECT COUNT(*) 
                FROM urls u 
                JOIN shortcodes s ON u.id = s.url_id
            """)
            total_count = cur.fetchone()[0]
            
            # Calculate total pages
            total_pages = (total_count + limit - 1) // limit
            
            # Get paginated results
            cur.execute("""
                SELECT 
                    s.code as short_code,
                    u.long_url,
                    u.created_at
                FROM urls u
                JOIN shortcodes s ON u.id = s.url_id
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            rows = cur.fetchall()
            
            # Format the response
            items = []
            for row in rows:
                short_code, long_url, created_at = row
                items.append({
                    'id': short_code,
                    'shortUrl': f"{self.base_url}/{short_code}",
                    'longUrl': long_url,
                    'clickCount': 0  # Default to 0 until clicks table is implemented
                })
            
            response = {
                'page': page,
                'limit': limit,
                'totalPages': total_pages,
                'totalItems': total_count,
                'items': items
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            print(f"Error in get_urls: {e}")
            return jsonify({
                'error': 'internal_error',
                'message': 'An unexpected error occurred while retrieving URLs'
            }), 500
            
        finally:
            cur.close()
            conn.close()
    
    def create_short_url(self):  # Fixed: Added self parameter
        """POST /v1/urls - Create a new short URL"""
        try:
            data = request.get_json()
            
            if not data or 'longUrl' not in data:
                return jsonify({
                    'error': 'validation_error',
                    'message': 'longUrl is required'
                }), 400
            
            long_url = data['longUrl']
            custom_code = data.get('customCode')
            
            # Basic URL validation
            if not long_url.startswith(('http://', 'https://')):
                return jsonify({
                    'error': 'validation_error',
                    'message': 'URL must start with http:// or https://'
                }), 400
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            try:
                # Check if custom code is provided and available
                if custom_code:
                    cur.execute("SELECT id FROM shortcodes WHERE code = %s", (custom_code,))
                    if cur.fetchone():
                        return jsonify({
                            'error': 'conflict_error',
                            'message': 'Custom code already exists'
                        }), 409
                    short_code = custom_code
                else:
                    # Generate unique short code
                    while True:
                        short_code = self.generate_code()
                        cur.execute("SELECT id FROM shortcodes WHERE code = %s", (short_code,))
                        if not cur.fetchone():
                            break
                
                # Insert URL
                cur.execute(
                    "INSERT INTO urls (long_url) VALUES (%s) RETURNING id",
                    (long_url,)
                )
                url_id = cur.fetchone()[0]
                
                # Insert shortcode
                cur.execute(
                    "INSERT INTO shortcodes (url_id, code) VALUES (%s, %s)",
                    (url_id, short_code)
                )
                
                conn.commit()
                
                return jsonify({
                    'id': short_code,
                    'shortUrl': f"{self.base_url}/{short_code}",
                    'longUrl': long_url,
                    'clickCount': 0
                }), 201
                
            except Exception as e:
                conn.rollback()
                print(f"Database error in create_short_url: {e}")
                return jsonify({
                    'error': 'internal_error',
                    'message': 'Failed to create short URL'
                }), 500
                
            finally:
                cur.close()
                conn.close()
                
        except Exception as e:
            print(f"Error in create_short_url: {e}")
            return jsonify({
                'error': 'internal_error',
                'message': 'An unexpected error occurred'
            }), 500
    
    def get_url(self, id):  # Fixed: Added self parameter and id parameter
        """GET /v1/urls/{id} - Get a specific URL by ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT u.long_url, s.code 
                FROM urls u
                JOIN shortcodes s ON u.id = s.url_id
                WHERE s.code = %s
            """, (id,))
            
            result = cur.fetchone()
            
            if not result:
                return jsonify({
                    'error': 'not_found',
                    'message': 'URL not found'
                }), 404
            
            long_url, short_code = result
            
            return jsonify({
                'id': short_code,
                'shortUrl': f"{self.base_url}/{short_code}",
                'longUrl': long_url,
                'clickCount': 0
            }), 200
            
        except Exception as e:
            print(f"Error in get_url: {e}")
            return jsonify({
                'error': 'internal_error',
                'message': 'An unexpected error occurred'
            }), 500
            
        finally:
            cur.close()
            conn.close()
    
    def redirect_to_original_url(self, id):  # Fixed: Added self parameter, id parameter, and corrected name
        """GET /{id}/redirect - Redirect to original URL"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT u.long_url 
                FROM urls u
                JOIN shortcodes s ON u.id = s.url_id
                WHERE s.code = %s
            """, (id,))
            
            result = cur.fetchone()
            
            if not result:
                return jsonify({
                    'error': 'not_found',
                    'message': 'Short URL not found'
                }), 404
            
            long_url = result[0]
            
            # TODO: Increment click count here
            
            return redirect(long_url, code=302)
            
        except Exception as e:
            print(f"Error in redirect_to_original_url: {e}")
            return jsonify({
                'error': 'internal_error',
                'message': 'An unexpected error occurred'
            }), 500
            
        finally:
            cur.close()
            conn.close()