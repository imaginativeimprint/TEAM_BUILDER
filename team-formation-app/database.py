import os
from libsql_client import create_client

# Turso configuration - from environment variables
TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')

def get_db():
    """Get database connection for Turso using HTTP client"""
    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        raise Exception("Turso credentials not configured")
    
    # Create HTTP client - no native binaries needed!
    client = create_client(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )
    return client

def init_db():
    """Initialize database tables in Turso"""
    try:
        client = get_db()
        
        # Create teams table
        client.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                team_number TEXT UNIQUE NOT NULL,
                secret_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create team_members table
        client.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                usn TEXT NOT NULL,
                name TEXT NOT NULL,
                last_three TEXT NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams (id),
                UNIQUE(team_id, usn)
            )
        ''')
        
        print("Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

# Helper for queries
def query_db(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a query and return results"""
    client = get_db()
    if params:
        result = client.execute(query, params)
    else:
        result = client.execute(query)
    
    if fetch_one:
        rows = result.fetchall()
        return rows[0] if rows else None
    elif fetch_all:
        return result.fetchall()
    return result
