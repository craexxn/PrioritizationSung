import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/GUIController')))


from settings_window import SettingsWindow

@pytest.fixture
def mock_controller():
    """Fixture to create a mock controller."""
    mock = MagicMock()
    mock.root = tk.Tk()
    mock.db_path = ":memory:"
    mock.current_user_id = 1
    return mock


@pytest.fixture
def settings_window(mock_controller):
    """Fixture to initialize the SettingsWindow with a mock controller."""
    window = SettingsWindow(mock_controller)
    yield window
    window.destroy()


@patch("settings_window.sqlite3.connect")
def test_load_settings_existing(mock_connect, settings_window):
    """Tests loading settings when settings already exist in the database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock existing settings
    mock_cursor.fetchone.return_value = (7, 1, 0, 15, 1, 'High', 'Low', 'High')

    # Action: Load settings
    settings_window.load_settings()

    # Assertions: Verify settings are loaded correctly
    assert settings_window.notification_interval_var.get() == 7
    assert settings_window.notifications_enabled_var.get() is True
    assert settings_window.auto_archive_var.get() is True
    assert settings_window.auto_delete_var.get() is False
    assert settings_window.auto_delete_interval_var.get() == 15
    assert settings_window.default_importance_var.get() == 'High'
    assert settings_window.default_urgency_var.get() == 'Low'
    assert settings_window.default_fitness_var.get() == 'High'


@patch("settings_window.sqlite3.connect")
def test_load_settings_default(mock_connect, settings_window):
    """Tests loading default settings when no settings exist in the database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock no existing settings
    mock_cursor.fetchone.return_value = None

    # Action: Load settings
    settings_window.load_settings()

    # Assertions: Verify default settings are loaded correctly
    assert settings_window.notification_interval_var.get() == 1
    assert settings_window.notifications_enabled_var.get() is True
    assert settings_window.auto_archive_var.get() is False
    assert settings_window.auto_delete_var.get() is False
    assert settings_window.auto_delete_interval_var.get() == 30
    assert settings_window.default_importance_var.get() == 'Low'
    assert settings_window.default_urgency_var.get() == 'Low'
    assert settings_window.default_fitness_var.get() == 'Low'


@patch("settings_window.sqlite3.connect")
def test_save_settings(mock_connect, settings_window):
    """Tests saving settings to the database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Set mock settings
    settings_window.notification_interval_var.set(5)
    settings_window.notifications_enabled_var.set(True)
    settings_window.auto_archive_var.set(False)
    settings_window.auto_delete_var.set(True)
    settings_window.auto_delete_interval_var.set(20)
    settings_window.default_importance_var.set('High')
    settings_window.default_urgency_var.set('High')
    settings_window.default_fitness_var.set('Low')

    # Action: Save settings
    settings_window.save_settings()

    # Assertions: Verify correct arguments are passed
    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args[0]

    # Verify the SQL statement structure
    assert "UPDATE settings" in query
    assert "SET notification_interval = ?" in query
    assert "WHERE user_id = ?" in query

    # Verify the parameters
    expected_params = (5, 0, 1, 20, 1, 'High', 'High', 'Low', settings_window.user_id)
    assert params == expected_params, f"Expected parameters {expected_params}, but got {params}"