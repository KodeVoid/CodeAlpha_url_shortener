from app.connect_db import get_db_connection
def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id SERIAL PRIMARY KEY,
        long_url TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shortcodes (
        id SERIAL PRIMARY KEY,
        code VARCHAR(10) UNIQUE NOT NULL,
        url_id INT REFERENCES urls(id) ON DELETE CASCADE,
        creator_id INT NULL, -- optional: who created this code
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_shortcodes_url_id ON shortcodes(url_id);
    """)
    
    conn.commit()
    cur.execute("SELECT version();")
    print(cur.fetchone())
    cur.close()
    conn.close()


setup_database()