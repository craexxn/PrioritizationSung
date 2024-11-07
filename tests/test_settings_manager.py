import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/SettingsManager')))

from settings_manager import SettingsManager


@pytest.fixture
def setup_settings_manager():
    # Erstellen einer temporären Datenbank für den Test
    db_path = 'test_settings.db'
    manager = SettingsManager(db_path)
    yield manager

    # Entferne die temporäre Datenbank nach dem Test
    os.remove(db_path)


def test_save_and_get_settings(setup_settings_manager):
    """
    Test that settings are saved and retrieved correctly.
    """
    manager = setup_settings_manager
    default_priorities = {"importance": "HIGH", "urgency": "LOW", "fitness": "HIGH"}
    manager.save_settings(notification_interval=2, auto_archive=False, auto_delete=True, notifications_enabled=True,
                          default_priorities=default_priorities)

    # Abrufen und Überprüfen der gespeicherten Einstellungen
    settings = manager.get_settings()
    assert settings["notification_interval"] == 2
    assert settings["auto_archive"] is False
    assert settings["auto_delete"] is True
    assert settings["notifications_enabled"] is True
    assert settings["default_priorities"] == default_priorities


def test_update_default_priorities(setup_settings_manager):
    """
    Test that the default priorities can be updated correctly.
    """
    manager = setup_settings_manager
    new_priorities = {"importance": "LOW", "urgency": "HIGH", "fitness": "MEDIUM"}

    # Aktualisieren der Standardprioritäten
    manager.update_default_priorities(new_priorities)
    settings = manager.get_settings()

    assert settings["default_priorities"] == new_priorities


def test_toggle_notifications_enabled(setup_settings_manager):
    """
    Test enabling and disabling notifications.
    """
    manager = setup_settings_manager

    # Benachrichtigungen deaktivieren
    manager.update_notifications_enabled(False)
    settings = manager.get_settings()
    assert settings["notifications_enabled"] is False

    # Benachrichtigungen aktivieren
    manager.update_notifications_enabled(True)
    settings = manager.get_settings()
    assert settings["notifications_enabled"] is True
