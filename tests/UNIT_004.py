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
    """Fixture to create a temporary SQLite database with the 'users' table."""
    conn = sqlite3.connect(":memory:")  # Use in-memory database for tests
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def mock_controller(initialize_database):
    """Mock for the application controller."""
    mock = MagicMock()
    mock.root = tk.Tk()  # Tkinter root window for the login window
    mock.db_path = ":memory:"  # Use the in-memory database for tests
    return mock


@pytest.fixture
def login_window(mock_controller):
    """Fixture for initializing the LoginWindow."""
    window = LoginWindow(mock_controller)
    # Overwrite user_repo connection to use the initialized database
    window.user_repo.conn = mock_controller.db_path  # Patch UserRepository db_path
    yield window
    window.destroy()  # Clean up the Tkinter window after the test


def test_validate_input_valid(login_window):
    """Tests validate_input with valid inputs."""
    assert login_window.validate_input("ValidUser123", "password123") is True


def test_validate_input_invalid_username(login_window):
    """Tests validate_input with an invalid username."""
    assert login_window.validate_input("ab", "password123") is False
    assert login_window.validate_input("InvalidUser!", "password123") is False
    assert login_window.validate_input("", "password123") is False


def test_validate_input_invalid_password(login_window):
    """Tests validate_input with an invalid password."""
    assert login_window.validate_input("ValidUser123", "s") is False
    assert login_window.validate_input("ValidUser123", "") is False


@patch("login_window.UserRepository")
def test_login_success(mock_user_repo, login_window, initialize_database):
    """Tests a successful login."""
    # Insert a user into the temporary database
    conn = initialize_database
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password_hash) VALUES (?, ?)
    ''', ("ValidUser123", "hashed_password"))
    conn.commit()

    # Mock UserRepository
    mock_user = MagicMock()
    mock_user.check_password.return_value = True
    mock_user.id = 1
    mock_user_repo.return_value.get_user_by_username.return_value = mock_user

    # Set mock inputs
    login_window.username_entry.get = MagicMock(return_value="ValidUser123")
    login_window.password_entry.get = MagicMock(return_value="password123")

    # Action
    login_window.login()

    # Assertions
    assert login_window.controller.current_user == "ValidUser123", "Current user not set correctly."
    assert login_window.controller.current_user_id == 1, "User ID not set correctly."


@patch("login_window.UserRepository")
def test_login_failure(mock_user_repo, login_window):
    """Tests login with invalid credentials."""
    # Mock UserRepository to return no user
    mock_user_repo.return_value.get_user_by_username.return_value = None

    # Set mock inputs
    login_window.username_entry.get = MagicMock(return_value="InvalidUser")
    login_window.password_entry.get = MagicMock(return_value="password123")

    # Mock messagebox to avoid actual GUI interaction
    with patch("tkinter.messagebox.showerror") as mock_messagebox:
        login_window.login()
        mock_messagebox.assert_called_once_with("Error", "Invalid username or password.")