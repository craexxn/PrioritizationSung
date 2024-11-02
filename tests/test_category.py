import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Category')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))

from category import Category
from task import Task, Priority
from datetime import date, timedelta



def test_category_creation():
    """
    Test the creation of a Category instance and check if attributes are set correctly.
    """
    category = Category(name="High Importance & High Urgency", description="Urgent and critical tasks")

    assert category.name == "High Importance & High Urgency"
    assert category.description == "Urgent and critical tasks"
    assert category.get_tasks() == []


def test_add_task():
    """
    Test adding a task to the category.
    """
    category = Category(name="General Tasks")
    task = Task(
        title="Review project plan",
        due_date=date.today() + timedelta(days=5),
        importance=Priority.LOW,
        urgency=Priority.HIGH,
        fitness=Priority.HIGH
    )

    category.add_task(task)

    assert len(category.get_tasks()) == 1
    assert category.get_tasks()[0] == task


def test_remove_task():
    """
    Test removing a task from the category.
    """
    category = Category(name="General Tasks")
    task = Task(
        title="Complete documentation",
        due_date=date.today() + timedelta(days=2),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.LOW
    )

    category.add_task(task)
    assert len(category.get_tasks()) == 1

    category.remove_task(task)
    assert len(category.get_tasks()) == 0
    assert task not in category.get_tasks()
