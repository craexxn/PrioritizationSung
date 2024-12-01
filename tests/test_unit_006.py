import os
import sys
import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/GUIController')))

from task_editor import TaskEditor

# Mocks for Priority and Status
class MockPriority:
    LOW = "Low"
    HIGH = "High"

class MockStatus:
    OPEN = "Open"
    COMPLETED = "Completed"

@pytest.fixture
def mock_controller():
    """Mock for the application controller."""
    controller = MagicMock()
    controller.root = tk.Tk()
    controller.db_path = ":memory:"
    controller.current_user_id = 1
    return controller

@pytest.fixture
def task_editor(mock_controller):
    """Fixture for initializing TaskEditor."""
    editor = TaskEditor(controller=mock_controller, title="Edit Task")
    yield editor
    editor.destroy()

def test_save_task_valid_input(task_editor):
    """Tests saving a task with valid input."""
    # Mock user input
    task_editor.title_entry.insert(0, "Valid Task Title")
    task_editor.description_text.insert("1.0", "This is a valid description.")
    task_editor.due_date_entry.insert(0, (datetime.today().date() + timedelta(days=1)).strftime("%Y-%m-%d"))
    task_editor.importance_combo.set(MockPriority.HIGH)
    task_editor.urgency_combo.set(MockPriority.LOW)
    task_editor.fitness_combo.set(MockPriority.HIGH)

    with patch("task_editor.sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Call save_task
        task_editor.save_task()

        # Verify database interaction
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

def test_mark_task_open():
    """Tests marking a task as open."""
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Test Task"
    mock_task.status = MockStatus.COMPLETED

    mock_controller = MagicMock()
    mock_controller.db_path = ":memory:"

    with patch("task_editor.sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Call mark_task_open
        TaskEditor.mark_task_open(mock_task, mock_controller)

        # Verify database interaction
        mock_cursor.execute.assert_called_once_with(
            '''
                UPDATE tasks
                SET status = ?
                WHERE id = ?
            ''', (MockStatus.OPEN, mock_task.id)
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
