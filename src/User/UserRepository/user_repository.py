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

    def __init__(self, db_path='database.db'):
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
        """
        Retrieves a user from the database by username.

        :param username: The username to search for.
        :return: A User instance if found, otherwise None.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Benutzer erstellen, ohne das Passwort erneut zu hashen
            user = User(username=row[1], password="")
            user.password_hash = row[2]  # Direkt den Hash setzen
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
