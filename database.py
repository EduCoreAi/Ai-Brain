import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Set up database path
DB_PATH = Path(__file__).parent.parent / "data" / "ai-brain.db"

def init_db():
    # Ensure the data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    # Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  prompt TEXT,
                  response TEXT,
                  rating INTEGER,
                  correction TEXT,
                  timestamp DATETIME)''')
    # Ingested documents table
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT,
                  content TEXT,
                  domain TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def log_feedback(prompt, response, rating, correction):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''INSERT INTO feedback 
                 (prompt, response, rating, correction, timestamp)
                 VALUES (?, ?, ?, ?, ?)''',
              (prompt, response, rating, correction, datetime.now()))
    conn.commit()
    conn.close()

def log_document(filename, content, domain):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''INSERT INTO documents 
                 (filename, content, domain, timestamp)
                 VALUES (?, ?, ?, ?)''',
              (filename, content, domain, datetime.now()))
    conn.commit()
    conn.close()

def get_feedback(limit=100):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT * FROM feedback ORDER BY timestamp DESC LIMIT ?', (limit,))
    data = c.fetchall()
    conn.close()
    return data

def get_documents(domain=None, limit=100):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    if domain:
        c.execute('SELECT * FROM documents WHERE domain=? ORDER BY timestamp DESC LIMIT ?', (domain, limit))
    else:
        c.execute('SELECT * FROM documents ORDER BY timestamp DESC LIMIT ?', (limit,))
    data = c.fetchall()
    conn.close()
    return data
