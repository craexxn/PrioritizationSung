import sys
import os

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/User')))

from user import User


def test_user_creation():
    """
    Test the creation of a User instance and check if attributes are set correctly.
    """
    user = User(username="testuser", password="securepassword123")

    assert user.username == "testuser"
    # Prüfen, ob das Passwort gehasht ist (sollte nicht im Klartext gespeichert sein)
    assert user.password_hash != "securepassword123"
    # Prüfen, ob das Passwort-Hashing korrekt funktioniert
    assert len(user.password_hash) == 64  # SHA-256 Hash-Länge


def test_check_password():
    """
    Test the check_password method to ensure it correctly verifies passwords.
    """
    user = User(username="testuser", password="mypassword")

    # Richtiges Passwort sollte True zurückgeben
    assert user.check_password("mypassword") == True
    # Falsches Passwort sollte False zurückgeben
    assert user.check_password("wrongpassword") == False


def test_password_hash_is_consistent():
    """
    Test that the password hash is consistent for the same input.
    """
    user1 = User(username="user1", password="samepassword")
    user2 = User(username="user2", password="samepassword")

    # Beide Benutzer sollten den gleichen Hash haben, da das Passwort gleich ist
    assert user1.password_hash == user2.password_hash
