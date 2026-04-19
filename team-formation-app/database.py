import os
from libsql_client import create_client
import sqlite3

# Turso configuration - from environment variables
TURSO_DATABASE_URL = os.environ.get('libsql://team-formation-app-imaginativeimprint.aws-ap-south-1.turso.io

')
TURSO_AUTH_TOKEN = os.environ.get('eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NzY1NjU1MzEsImlkIjoiMDE5ZGEzOGUtNDIwMS03NDVmLWI5MmMtYWI0YWJhZGQ3MzJmIiwicmlkIjoiZTc1NzU5OTUtYzg4NS00NTcxLWFmZGUtZWJhM2JmNjBmZTNjIn0.EYTnIC_t2WMmpl32Fbp5kbelLPg1X0zhVlIGCdFm20g4doZ569XUzGEW4GYBzw0VEWvI2HQ9lR3v9uyqErMUCQ')

class TursoConnection:
    """A wrapper that makes Turso behave like sqlite3.Connection"""
    
    def __init__(self, client):
        self.client = client
        self.row_factory = None
        
    def cursor(self):
        return TursoCursor(self.client, self)
    
    def commit(self):
        # Turso auto-commits, but we'll keep this for compatibility
        pass
    
    def rollback(self):
        # Turso doesn't support rollback in the same way, but we'll keep for compatibility
        pass
    
    def close(self):
        # Turso client doesn't need explicit closing
        pass
    
    def execute(self, sql, parameters=None):
        cursor = self.cursor()
        if parameters:
            return cursor.execute(sql, parameters)
        return cursor.execute(sql)
    
    def executemany(self, sql, seq_of_parameters):
        cursor = self.cursor()
        return cursor.executemany(sql, seq_of_parameters)

class TursoCursor:
    """A wrapper that makes Turso results behave like sqlite3.Cursor"""
    
    def __init__(self, client, connection):
        self.client = client
        self.connection = connection
        self.last_result = None
        self.rowcount = -1
        
    def execute(self, sql, parameters=None):
        try:
            if parameters:
                # Convert parameters to list if needed
                if isinstance(parameters, dict):
                    # For named parameters, we need to handle differently
                    # But most of your code uses positional parameters (?, ?)
                    params_list = []
                    for key in sorted(parameters.keys()):
                        params_list.append(parameters[key])
                    self.last_result = self.client.execute(sql, params_list)
                else:
                    self.last_result = self.client.execute(sql, parameters)
            else:
                self.last_result = self.client.execute(sql)
            
            # Update rowcount (approximate)
            if self.last_result and hasattr(self.last_result, 'rows_affected'):
                self.rowcount = self.last_result.rows_affected
            else:
                self.rowcount = -1
                
            return self
        except Exception as e:
            print(f"Turso execute error: {e}")
            raise e
    
    def executemany(self, sql, seq_of_parameters):
        for parameters in seq_of_parameters:
            self.execute(sql, parameters)
        return self
    
    def fetchone(self):
        if self.last_result:
            rows = self.last_result.fetchall()
            if rows:
                row = rows[0]
                # Convert to sqlite3.Row-like object
                return self._row_to_dict(row)
        return None
    
    def fetchall(self):
        if self.last_result:
            rows = self.last_result.fetchall()
            return [self._row_to_dict(row) for row in rows]
        return []
    
    def _row_to_dict(self, row):
        """Convert Turso row to a dictionary that behaves like sqlite3.Row"""
        if hasattr(row, 'keys'):
            # Create a simple object that supports indexing and key access
            class RowWrapper:
                def __init__(self, data, keys):
                    self._data = data
                    self._keys = keys
                    
                def __getitem__(self, key):
                    if isinstance(key, int):
                        return self._data[key]
                    else:
                        # Find column index by name
                        try:
                            idx = list(self._keys).index(key)
                            return self._data[idx]
                        except ValueError:
                            raise KeyError(key)
                            
                def __len__(self):
                    return len(self._data)
                
                def keys(self):
                    return self._keys
                
                def __getattr__(self, name):
                    # Allow attribute access like row.column_name
                    try:
                        idx = list(self._keys).index(name)
                        return self._data[idx]
                    except ValueError:
                        raise AttributeError(name)
            
            return RowWrapper(row, row.keys())
        return row
    
    @property
    def lastrowid(self):
        """Get last inserted row ID"""
        if self.last_result and hasattr(self.last_result, 'last_insert_rowid'):
            return self.last_result.last_insert_rowid
        return None

def get_db():
    """Get database connection compatible with sqlite3"""
    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        raise Exception("Turso credentials not configured. Please set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN environment variables.")
    
    # Create client for Turso
    client = create_client(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )
    
    # Return wrapped connection
    conn = TursoConnection(client)
    conn.row_factory = sqlite3.Row  # For compatibility
    return conn

def init_db():
    """Initialize database tables in Turso"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Create teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                team_number TEXT UNIQUE NOT NULL,
                secret_key TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create team_members table
        cursor.execute('''
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
        
        print("✅ Database initialized successfully in Turso")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
