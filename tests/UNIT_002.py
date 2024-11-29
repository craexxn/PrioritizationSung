import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/GUIController')))

from archive_viewer import ArchiveViewer
from task import Task, Priority, Status

@pytest.fixture
def mock_controller():
    """Mock for the application controller."""
    mock = MagicMock()
    mock.db_path = ":memory:"
    mock.current_user_id = 1
    return mock

@pytest.fixture
def archive_viewer(mock_controller):
    """Fixture to initialize the ArchiveViewer."""
    return ArchiveViewer(mock_controller)

@patch("sqlite3.connect")
def test_load_archived_tasks(mock_connect, archive_viewer):
    """Tests loading of archived tasks into the UI."""
    # Mock database setup
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Define test data
    mock_cursor.fetchall.return_value = [
        ("Task 1", "Description 1", "2024-01-01", "High", "Low", "High", "Completed"),
        ("Task 2", "Description 2", "2024-01-05", "Low", "High", "Low", "Completed"),
    ]

    print("Mock setup complete")  # Debug message

    # Action: Load archived tasks
    archive_viewer.load_archived_tasks()

    print("Tasks loaded")  # Debug message

    # Assertions
    assert len(archive_viewer.archived_tasks) == 2, "Archived tasks were not loaded correctly."
    assert archive_viewer.archived_listbox.size() == 2, "UI ListBox was not updated with the correct number of tasks."
    assert archive_viewer.archived_tasks[0].title == "Task 1", "First task title mismatch."
    assert archive_viewer.archived_tasks[1].title == "Task 2", "Second task title mismatch."