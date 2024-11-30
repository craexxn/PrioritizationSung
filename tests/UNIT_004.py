import os
import sys
import pytest
import sqlite3
from unittest.mock import MagicMock, patch
import tkinter as tk

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/GUIController')))

from login_window import LoginWindow


@pytest.fixture
def initialize_database():
    """Initializes an in-memory database and creates the users table."""
    conn = sqlite3.connect(":memory:")  # Use an in-memory database for testing
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def mock_controller():
    """Mock for the application controller."""
    mock = MagicMock()
    mock.root = tk.Tk()  # Create a Tkinter root window
    mock.current_user = None
    mock.current_user_id = None
    return mock


@pytest.fixture
def login_window(mock_controller):
    """Fixture to initialize the LoginWindow with a mock controller."""
    with patch("login_window.UserRepository") as MockUserRepository:
        mock_user_repo = MockUserRepository.return_value
        window = LoginWindow(mock_controller)
        window.user_repo = mock_user_repo  # Replace the real UserRepository with a mock
        yield window
        window.destroy()  # Clean up the Tkinter window after the test


def test_validate_input_valid(login_window):
    """Tests validate_input with valid inputs."""
    assert login_window.validate_input("ValidUser123", "securepassword") is True


def test_validate_input_invalid_username(login_window):
    """Tests validate_input with invalid usernames."""
    assert login_window.validate_input("", "password123") is False
    assert login_window.validate_input("ab", "password123") is False
    assert login_window.validate_input("Invalid@User", "password123") is False


def test_validate_input_invalid_password(login_window):
    """Tests validate_input with invalid passwords."""
    assert login_window.validate_input("ValidUser123", "") is False
    assert login_window.validate_input("ValidUser123", "pw") is False


def test_login_success(login_window):
    """Tests successful login."""
    # Mock the UserRepository's get_user_by_username method
    mock_user = MagicMock()
    mock_user.check_password.return_value = True
    mock_user.id = 1
    login_window.user_repo.get_user_by_username.return_value = mock_user

    # Mock input values
    login_window.username_entry.get = MagicMock(return_value="ValidUser123")
    login_window.password_entry.get = MagicMock(return_value="password123")

    # Action
    login_window.login()

    # Assertions
    assert login_window.controller.current_user == "ValidUser123"
    assert login_window.controller.current_user_id == 1
    login_window.controller.load_tasks.assert_called_once()


def test_login_failure(login_window):
    """Tests login failure with invalid credentials."""
    # Mock the UserRepository to return None for invalid credentials
    login_window.user_repo.get_user_by_username.return_value = None

    # Mock input values
    login_window.username_entry.get = MagicMock(return_value="InvalidUser")
    login_window.password_entry.get = MagicMock(return_value="wrongpassword")

    # Mock the messagebox to avoid GUI interaction
    with patch("tkinter.messagebox.showerror") as mock_messagebox:
        login_window.login()
        mock_messagebox.assert_called_once_with("Error", "Invalid username or password.")