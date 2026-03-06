import sqlite3
import os

def get_db():
    # Create instance folder if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    db_path = os.path.join('instance', 'teams.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Create instance folder if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    db = get_db()
    cursor = db.cursor()
    
    # Create teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            team_number TEXT UNIQUE NOT NULL,
            secret_key TEXT NOT NULL,
            created_at TIMESTAMP
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
    
    db.commit()
    db.close()
    print("Database initialized successfully")