import os
import sys
import pytest
import tkinter as tk
from datetime import datetime
from unittest.mock import MagicMock

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/GUIController')))

from filter_controller import FilterController


@pytest.fixture
def mock_gui_controller():
    """Mock for the GUI controller."""
    mock = MagicMock()
    return mock


@pytest.fixture
def filter_controller_with_root(mock_gui_controller):
    """Fixture for initializing the FilterController with a Tkinter root window."""
    root = tk.Tk()  # Initialize Tkinter root window
    mock_gui_controller.root = root  # Assign root to the mock controller
    controller = FilterController(mock_gui_controller)
    yield controller
    root.destroy()  # Destroy the Tkinter root window after the test


def test_apply_filters_success(filter_controller_with_root):
    """Tests that apply_filters correctly collects and applies filters."""
    controller = filter_controller_with_root

    # Set mock GUI inputs
    controller.search_entry.get = MagicMock(return_value="Test Task")
    controller.importance_var.get = MagicMock(return_value="High")
    controller.urgency_var.get = MagicMock(return_value="Low")
    controller.fitness_var.get = MagicMock(return_value="All")
    controller.due_date_entry.get = MagicMock(return_value="2024-12-01")

    # Mock the load_tasks method in the GUI controller
    controller.gui_controller.load_tasks = MagicMock()

    # Action: Apply filters
    controller.apply_filters()

    # Assertions: Check if filters are collected and passed correctly
    expected_filters = {
        "search": "Test Task",
        "importance": "High",
        "urgency": "Low",
        "due_date": datetime.strptime("2024-12-01", "%Y-%m-%d").date()
    }
    assert controller.filters == expected_filters, "Filters were not collected correctly."
    controller.gui_controller.load_tasks.assert_called_once_with(expected_filters)


def test_reset_filters(filter_controller_with_root):
    """Tests that reset_filters clears all filters and reloads the task list."""
    controller = filter_controller_with_root

    # Set mock GUI inputs
    controller.search_entry.delete = MagicMock()
    controller.importance_var.set = MagicMock()
    controller.urgency_var.set = MagicMock()
    controller.fitness_var.set = MagicMock()
    controller.gui_controller.load_tasks = MagicMock()

    # Action: Reset filters
    controller.reset_filters()

    # Assertions: Check if all inputs are reset
    controller.search_entry.delete.assert_called_once_with(0, tk.END)
    controller.importance_var.set.assert_called_once_with("All")
    controller.urgency_var.set.assert_called_once_with("All")
    controller.fitness_var.set.assert_called_once_with("All")
    controller.gui_controller.load_tasks.assert_called_once()