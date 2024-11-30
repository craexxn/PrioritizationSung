import os
import sys
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/NotificationManager')))

from notification_manager import NotificationManager


class MockTask:
    """Mock class for Task objects."""

    def __init__(self, title, due_date):
        self.title = title
        self.due_date = due_date


@pytest.fixture
def mock_settings_manager():
    """Fixture for mocking SettingsManager."""
    mock = MagicMock()
    mock.get_settings.return_value = {
        "notifications_enabled": True,
        "notification_interval": 3
    }
    return mock


@pytest.fixture
def notification_manager(mock_settings_manager):
    """Fixture for initializing NotificationManager."""
    return NotificationManager(settings_manager=mock_settings_manager)


def test_schedule_notifications_within_interval(notification_manager):
    """Tests scheduling notifications for tasks due within the interval."""
    tasks = [
        MockTask("Task 1", date.today() + timedelta(days=1)),
        MockTask("Task 2", date.today() + timedelta(days=2)),
        MockTask("Task 3", date.today() + timedelta(days=5))
    ]
    notifications = notification_manager.schedule_notifications(tasks)

    # Expect tasks 1 and 2 to have notifications scheduled
    assert len(notifications) == 2
    assert notifications[0]["task"].title == "Task 1"
    assert notifications[1]["task"].title == "Task 2"


def test_schedule_notifications_outside_interval(notification_manager):
    """Tests that tasks outside the interval are not scheduled for notifications."""
    tasks = [
        MockTask("Task 1", date.today() + timedelta(days=4)),
        MockTask("Task 2", date.today() + timedelta(days=6))
    ]
    notifications = notification_manager.schedule_notifications(tasks)

    # Expect no notifications to be scheduled
    assert len(notifications) == 0


def test_schedule_notifications_disabled(notification_manager, mock_settings_manager):
    """Tests that no notifications are scheduled when notifications are disabled."""
    # Disable notifications in settings
    mock_settings_manager.get_settings.return_value["notifications_enabled"] = False

    tasks = [
        MockTask("Task 1", date.today() + timedelta(days=1)),
        MockTask("Task 2", date.today() + timedelta(days=2))
    ]
    notifications = notification_manager.schedule_notifications(tasks)

    # Expect no notifications to be scheduled
    assert len(notifications) == 0
