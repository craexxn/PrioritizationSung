import sys
import os

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))

from task import Task, Priority, Status
from datetime import date, timedelta


def test_task_creation():
    """
    Test the creation of a Task instance and check if attributes are set correctly.
    """
    task = Task(
        title="Complete project documentation",
        due_date=date.today() + timedelta(days=7),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.HIGH,
        description="Finalize and review the project documentation."
    )

    assert task.title == "Complete project documentation"
    assert task.due_date == date.today() + timedelta(days=7)
    assert task.importance == Priority.HIGH
    assert task.urgency == Priority.LOW
    assert task.fitness == Priority.HIGH
    assert task.description == "Finalize and review the project documentation."
    assert task.status == Status.OPEN
    assert task.completed_date is None


def test_edit_task():
    """
    Test editing the attributes of a Task instance.
    """
    task = Task(
        title="Initial task title",
        due_date=date.today() + timedelta(days=3),
        importance=Priority.LOW,
        urgency=Priority.HIGH,
        fitness=Priority.LOW
    )

    # Edit task attributes
    new_due_date = date.today() + timedelta(days=10)
    task.edit_task(
        title="Updated task title",
        due_date=new_due_date,
        importance=Priority.HIGH,
        urgency=Priority.HIGH,
        fitness=Priority.HIGH,
        description="Updated description."
    )

    assert task.title == "Updated task title"
    assert task.due_date == new_due_date
    assert task.importance == Priority.HIGH
    assert task.urgency == Priority.HIGH
    assert task.fitness == Priority.HIGH
    assert task.description == "Updated description."


def test_mark_as_completed():
    """
    Test marking a Task instance as completed.
    """
    task = Task(
        title="Complete testing module",
        due_date=date.today() + timedelta(days=1),
        importance=Priority.HIGH,
        urgency=Priority.HIGH,
        fitness=Priority.HIGH
    )

    # Mark task as completed
    task.mark_as_completed()

    assert task.status == Status.COMPLETED
    assert task.completed_date == date.today()
