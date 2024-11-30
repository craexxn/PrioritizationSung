import os
import sys
import pytest

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/User')))

from user import User

def test_user_initialization():
    """Tests the initialization of a User object."""
    user = User(username="test_user", password="securepassword")

    assert user.username == "test_user"
    assert isinstance(user.password_hash, str), "Password hash should be a string"
    assert len(user.password_hash) == 64, "SHA-256 hash should have a length of 64 characters"

def test_hash_password():
    """Tests the hash_password method."""
    user = User(username="test_user", password="securepassword")

    expected_hash = user.hash_password("securepassword")
    assert user.password_hash == expected_hash, "Password hash does not match expected value"

def test_check_password():
    """Tests the check_password method."""
    user = User(username="test_user", password="securepassword")

    # Correct password
    assert user.check_password("securepassword"), "Password verification failed for correct password"

    # Incorrect password
    assert not user.check_password("wrongpassword"), "Password verification succeeded for incorrect password"
