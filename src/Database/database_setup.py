import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))

import sqlite3

def initialize_database():
    # Create a connection to the database file (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the tasks table with essential fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            importance TEXT,
            urgency TEXT,
            fitness TEXT,
            status TEXT,
            completed_date TEXT
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database and tasks table initialized successfully.")

# Run the database initialization
if __name__ == "__main__":
    initialize_database()