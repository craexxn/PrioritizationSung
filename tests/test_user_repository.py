import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/User')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/User/UserRepository')))

from user_repository import UserRepository
from user import User


# Fixture zum Setup einer temporären Datenbank für Tests
@pytest.fixture
def setup_database():
    # Erstellen einer temporären Datenbank
    db_path = 'test_database.db'
    repo = UserRepository(db_path)

    # Initialisiere die Datenbanktabelle für Benutzer
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    yield repo

    # Entferne die temporäre Datenbank nach dem Test
    os.remove(db_path)


def test_save_user(setup_database):
    """
    Test that a user is saved correctly in the database.
    """
    repo = setup_database
    user = User(username="testuser", password="securepassword")

    # Speichern des Benutzers in der Datenbank
    repo.save_user(user)

    # Benutzer aus der Datenbank abrufen
    retrieved_user = repo.get_user_by_username("testuser")
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.password_hash == user.password_hash


def test_get_user_by_username(setup_database):
    """
    Test retrieving a user by username.
    """
    repo = setup_database
    user = User(username="anotheruser", password="password123")

    # Speichern des Benutzers und Abrufen
    repo.save_user(user)
    retrieved_user = repo.get_user_by_username("anotheruser")

    assert retrieved_user is not None
    assert retrieved_user.username == "anotheruser"
    assert retrieved_user.password_hash == user.password_hash


def test_delete_user(setup_database):
    """
    Test that a user is deleted correctly from the database.
    """
    repo = setup_database
    user = User(username="user_to_delete", password="deletepassword")

    # Benutzer speichern und anschließend löschen
    repo.save_user(user)
    repo.delete_user("user_to_delete")

    # Überprüfen, dass der Benutzer entfernt wurde
    deleted_user = repo.get_user_by_username("user_to_delete")
    assert deleted_user is None
