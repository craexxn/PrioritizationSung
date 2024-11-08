import os
import sys
import pytest
import sqlite3
from datetime import date, timedelta

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/SettingsManager')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/NotificationManager')))

from notification_manager import NotificationManager
from settings_manager import SettingsManager
from task import Task, Priority, Status


@pytest.fixture
def setup_notification_manager():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Database/database.db'))
    settings_manager = SettingsManager(db_path=db_path)
    notification_manager = NotificationManager(settings_manager=settings_manager)

    # Initialize database with default settings
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM settings')
    cursor.execute('''
        INSERT INTO settings (id, notification_interval, notifications_enabled, auto_archive, auto_delete, default_priorities)
        VALUES (1, 2, 1, 1, 0, '{"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}')
    ''')
    conn.commit()
    conn.close()

    return notification_manager, settings_manager


def test_notification_enabled(setup_notification_manager):
    notification_manager, settings_manager = setup_notification_manager
    task = Task(
        title="Upcoming Task",
        description="This task is due soon.",
        due_date=date.today() + timedelta(days=2),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.LOW,
        status=Status.OPEN
    )

    notifications = notification_manager.schedule_notifications([task])
    assert len(notifications) == 1
    assert notifications[0]["task"].title == "Upcoming Task"


def test_notification_disabled(setup_notification_manager):
    notification_manager, settings_manager = setup_notification_manager
    settings_manager.update_notifications_enabled(False)

    task = Task(
        title="Disabled Notification Task",
        description="This task should not trigger a notification.",
        due_date=date.today() + timedelta(days=2),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.LOW,
        status=Status.OPEN
    )

    notifications = notification_manager.schedule_notifications([task])
    assert len(notifications) == 0


def test_notification_interval_update(setup_notification_manager):
    notification_manager, settings_manager = setup_notification_manager
    settings_manager.update_notification_interval(1)

    task = Task(
        title="Interval Update Task",
        description="This task is due soon.",
        due_date=date.today() + timedelta(days=2),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.LOW,
        status=Status.OPEN
    )

    notifications = notification_manager.schedule_notifications([task])
    assert len(notifications) == 0  # Notification should not trigger with interval set to 1 day