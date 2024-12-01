import sqlite3
import sys
import os

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../User')))

from user import User


class UserRepository:
    """
    UserRepository handles database operations for users.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            # Dynamically determine the database path based on the execution environment
            if getattr(sys, 'frozen', False):  # Running as an executable
                self.db_path = os.path.join(os.path.dirname(sys.executable), "database.db")
            else:  # Running as a script
                self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Database/database.db'))
        else:
            self.db_path = db_path

    def save_user(self, user: User):
        """
        Saves a user to the database.

        :param user: User instance to save.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', (user.username, user.password_hash))

        user.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def get_user_by_username(self, username: str) -> User:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            user = User(username=row[1], password="")
            user.password_hash = row[2]
            user.id = row[0]  # Assign the retrieved id to the user
            return user
        return None

    def delete_user(self, username: str):
        """
        Deletes a user from the database by username.

        :param username: The username of the user to delete.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        conn.close()
