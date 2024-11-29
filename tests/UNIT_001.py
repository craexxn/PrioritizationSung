import os
import sys
import sqlite3
import pytest
from datetime import date, timedelta

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/ArchiveManager')))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Database/database.db'))

from archive_manager import ArchiveManager
from task import Task, Status, Priority

# Fixture to set up a fresh ArchiveManager instance with a persistent database
@pytest.fixture
def setup_archive_manager():
    """
    Fixture to create a new ArchiveManager instance and ensure a clean database.
    """
    # Ensure tables are created in the actual database
    manager = ArchiveManager(DB_PATH)
    return manager

# Helper function to clear the archived_tasks table before each test run
def clear_archived_tasks_table():
    """
    Clears all entries from the archived_tasks table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM archived_tasks')
    conn.commit()
    conn.close()

# Run the clear function before each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    clear_archived_tasks_table()
    yield
    clear_archived_tasks_table()

def test_archive_task(setup_archive_manager):
    """
    Test that a completed task is correctly archived in the database.
    """
    manager = setup_archive_manager
    task = Task(
        title="Completed Task",
        description="A task that is completed.",
        due_date=date.today(),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.HIGH,
        status=Status.COMPLETED,
        completed_date=date.today() - timedelta(days=1)
    )

    # Archive the completed task
    manager.archive_task(task)

    # Verify the task is in the archived_tasks table
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM archived_tasks WHERE title = ?', (task.title,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None, "Task should be archived in the 'archived_tasks' table."

def test_archive_task_raises_error_for_incomplete_task(setup_archive_manager):
    """
    Test that an error is raised when attempting to archive a task that is not completed.
    """
    manager = setup_archive_manager
    task = Task(
        title="Incomplete Task",
        description="A task that is not completed.",
        due_date=date.today(),
        importance=Priority.LOW,
        urgency=Priority.HIGH,
        fitness=Priority.LOW,
        status=Status.OPEN  # Task is not completed
    )

    with pytest.raises(ValueError, match="Only completed tasks can be archived."):
        manager.archive_task(task)

def test_auto_archive_task(setup_archive_manager):
    """
    Test that a task is automatically archived after the specified period.
    """
    manager = setup_archive_manager
    task = Task(
        title="Auto Archive Task",
        description="A task that should be auto-archived.",
        due_date=date.today(),
        importance=Priority.LOW,
        urgency=Priority.HIGH,
        fitness=Priority.LOW,
        status=Status.COMPLETED,
        completed_date=date.today() - timedelta(days=8)
    )

    # Auto-archive the task if it has been completed for at least 7 days
    manager.auto_archive_task(task, days_until_archive=7)

    # Verify the task is in the archived_tasks table
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM archived_tasks WHERE title = ?', (task.title,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None, "Task should be auto-archived in the 'archived_tasks' table."

def test_auto_delete_task(setup_archive_manager):
    """
    Test that a task is automatically deleted from the archive after the specified period.
    """
    manager = setup_archive_manager
    task = Task(
        title="Auto Delete Task",
        description="A task that should be auto-deleted.",
        due_date=date.today(),
        importance=Priority.HIGH,
        urgency=Priority.HIGH,
        fitness=Priority.LOW,
        status=Status.COMPLETED,
        completed_date=date.today() - timedelta(days=40)
    )

    # Archive the task manually
    manager.archive_task(task)

    # Retrieve the task's ID from the archived_tasks table
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM archived_tasks WHERE title = ?', (task.title,))
    task_id = cursor.fetchone()[0]
    conn.close()

    # Manually set the task's ID and attempt auto-deletion after 30 days
    task.id = task_id
    manager.auto_delete_task(task, days_until_delete=30)

    # Verify the task has been deleted from the archived_tasks table
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM archived_tasks WHERE id = ?', (task.id,))
    result = cursor.fetchone()
    conn.close()

    assert result is None, "Task should be auto-deleted from the 'archived_tasks' table after 30 days."
