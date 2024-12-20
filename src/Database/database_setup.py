import sqlite3

def initialize_database():
    """
    Initializes the SQLite database.
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the tasks table if it does not exist, with a user_id column to link tasks to users
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
            completed_date TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create the users table if it does not exist, for user authentication and task linking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    # Create the archived_tasks table if it does not exist, including user_id for user-specific archiving
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            importance TEXT,
            urgency TEXT,
            fitness TEXT,
            status TEXT,
            completed_date TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create the settings table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            notification_interval INTEGER DEFAULT 1,
            auto_archive INTEGER DEFAULT 0,
            auto_delete INTEGER DEFAULT 0,
            auto_delete_interval INTEGER DEFAULT 30,
            notifications_enabled INTEGER DEFAULT 1,
            default_importance TEXT DEFAULT 'None',
            default_urgency TEXT DEFAULT 'None',
            default_fitness TEXT DEFAULT 'None',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')


    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database and tables initialized successfully.")

if __name__ == "__main__":
    initialize_database()
