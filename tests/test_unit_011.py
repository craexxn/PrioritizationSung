import os
import sys
import pytest
import sqlite3
from unittest.mock import MagicMock, patch

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/User')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/User/UserRepository')))

from user import User
from user_repository import UserRepository


@pytest.fixture
def in_memory_user_repository():
    """Fixture for setting up an in-memory UserRepository."""
    with patch("user_repository.sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        repo = UserRepository(db_path=":memory:")
        repo.connection = mock_conn
        yield repo, mock_cursor


def test_save_user(in_memory_user_repository):
    """Tests saving a user to the database."""
    repo, mock_cursor = in_memory_user_repository

    # Arrange
    user = User(username="test_user", password="securepassword")

    # Act
    repo.save_user(user)

    # Assert
    mock_cursor.execute.assert_called_once()
    called_args, called_kwargs = mock_cursor.execute.call_args

    # Normalize SQL strings by removing extra whitespaces and line breaks
    def normalize_sql(sql):
        return " ".join(sql.split())

    expected_sql = normalize_sql('''
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    ''')
    actual_sql = normalize_sql(called_args[0])
    assert expected_sql == actual_sql, f"Expected SQL: {expected_sql}, but got: {actual_sql}"

    # Check the parameters passed
    assert called_args[1] == (user.username, user.password_hash)




def test_get_user_by_username_existing(in_memory_user_repository):
    """Tests retrieving an existing user by username."""
    repo, mock_cursor = in_memory_user_repository

    # Arrange
    mock_cursor.fetchone.return_value = (1, "test_user", "hashed_password")

    # Act
    user = repo.get_user_by_username("test_user")

    # Assert
    assert user is not None
    assert user.username == "test_user"
    assert user.password_hash == "hashed_password"
    assert user.id == 1
    mock_cursor.execute.assert_called_once_with(
        'SELECT id, username, password_hash FROM users WHERE username = ?', ("test_user",)
    )


def test_get_user_by_username_non_existing(in_memory_user_repository):
    """Tests retrieving a non-existing user by username."""
    repo, mock_cursor = in_memory_user_repository

    # Arrange
    mock_cursor.fetchone.return_value = None

    # Act
    user = repo.get_user_by_username("non_existing_user")

    # Assert
    assert user is None
    mock_cursor.execute.assert_called_once_with(
        'SELECT id, username, password_hash FROM users WHERE username = ?', ("non_existing_user",)
    )


def test_delete_user(in_memory_user_repository):
    """Tests deleting a user by username."""
    repo, mock_cursor = in_memory_user_repository

    # Act
    repo.delete_user("test_user")

    # Assert
    mock_cursor.execute.assert_called_once_with(
        'DELETE FROM users WHERE username = ?', ("test_user",)
    )
