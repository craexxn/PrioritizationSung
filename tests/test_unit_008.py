import os
import sys
import pytest
import sqlite3
import json

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/SettingsManager')))

from settings_manager import SettingsManager

@pytest.fixture
def temp_database():
    """Fixture for creating a temporary database file."""
    db_path = "test_database.db"
    # Remove existing test database if present
    if os.path.exists(db_path):
        os.remove(db_path)
    yield db_path
    # Cleanup: Remove the test database after tests
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def settings_manager(temp_database):
    """Fixture for initializing SettingsManager with a temporary database."""
    return SettingsManager(temp_database)


def test_initialize_settings_table(settings_manager, temp_database):
    """Tests that the settings table is initialized correctly."""
    conn = sqlite3.connect(temp_database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "Settings table was not created."


def test_get_settings_default(settings_manager):
    """Tests retrieving default settings when no custom settings exist."""
    settings = settings_manager.get_settings()
    expected_settings = {
        "notification_interval": 1,
        "auto_archive": True,
        "auto_delete": False,
        "notifications_enabled": True,
        "default_priorities": {"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}
    }
    assert settings == expected_settings, "Default settings do not match expected values."


def test_save_and_get_custom_settings(settings_manager):
    """Tests saving and retrieving custom settings."""
    custom_settings = {
        "notification_interval": 3,
        "auto_archive": False,
        "auto_delete": True,
        "notifications_enabled": False,
        "default_priorities": {"importance": "HIGH", "urgency": "LOW", "fitness": "HIGH"}
    }
    settings_manager.save_settings(
        notification_interval=custom_settings["notification_interval"],
        auto_archive=custom_settings["auto_archive"],
        auto_delete=custom_settings["auto_delete"],
        notifications_enabled=custom_settings["notifications_enabled"],
        default_priorities=custom_settings["default_priorities"]
    )
    retrieved_settings = settings_manager.get_settings()
    assert retrieved_settings == custom_settings, "Retrieved settings do not match saved settings."


def test_update_notification_interval(settings_manager):
    """Tests updating the notification interval."""
    settings_manager.update_notification_interval(5)
    updated_settings = settings_manager.get_settings()
    assert updated_settings["notification_interval"] == 5, "Notification interval was not updated correctly."


def test_update_notifications_enabled(settings_manager):
    """Tests enabling or disabling notifications."""
    settings_manager.update_notifications_enabled(False)
    updated_settings = settings_manager.get_settings()
    assert updated_settings["notifications_enabled"] is False, "Notifications enabled status was not updated correctly."


def test_update_default_priorities(settings_manager):
    """Tests updating the default priorities."""
    new_priorities = {"importance": "HIGH", "urgency": "HIGH", "fitness": "LOW"}
    settings_manager.update_default_priorities(new_priorities)
    updated_settings = settings_manager.get_settings()
    assert updated_settings["default_priorities"] == new_priorities, "Default priorities were not updated correctly."