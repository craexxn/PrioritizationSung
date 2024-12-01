import os
import sys
import pytest
from datetime import date, timedelta

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))

from task import Task, Priority, Status


def test_task_initialization():
    """Tests the initialization of a Task object."""
    task = Task(
        title="Test Task",
        due_date=date.today() + timedelta(days=5),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.HIGH,
        description="A sample task for testing",
        status=Status.IN_PROGRESS,
        completed_date=None,
        task_id=1
    )

    assert task.id == 1
    assert task.title == "Test Task"
    assert task.due_date == date.today() + timedelta(days=5)
    assert task.importance == Priority.HIGH
    assert task.urgency == Priority.LOW
    assert task.fitness == Priority.HIGH
    assert task.description == "A sample task for testing"
    assert task.status == Status.IN_PROGRESS
    assert task.completed_date is None


def test_task_edit():
    """Tests the edit_task method."""
    task = Task(
        title="Initial Task",
        due_date=date.today(),
        importance=Priority.LOW,
        urgency=Priority.LOW,
        fitness=Priority.LOW
    )

    new_due_date = date.today() + timedelta(days=10)
    task.edit_task(
        title="Updated Task",
        due_date=new_due_date,
        importance=Priority.HIGH,
        urgency=Priority.HIGH,
        fitness=Priority.HIGH,
        description="Updated description"
    )

    assert task.title == "Updated Task"
    assert task.due_date == new_due_date
    assert task.importance == Priority.HIGH
    assert task.urgency == Priority.HIGH
    assert task.fitness == Priority.HIGH
    assert task.description == "Updated description"


def test_mark_as_completed():
    """Tests the mark_as_completed method."""
    task = Task(
        title="Complete Task",
        due_date=date.today(),
        importance=Priority.HIGH,
        urgency=Priority.HIGH,
        fitness=Priority.HIGH
    )

    task.mark_as_completed()

    assert task.status == Status.COMPLETED
    assert task.completed_date == date.today()
