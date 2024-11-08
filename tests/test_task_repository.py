import sys
import os
import sqlite3
import pytest
from datetime import date, timedelta

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/Task/TaskRepository')))

from task import Task, Priority, Status
from task_repository import TaskRepository


# Erstellen einer temporären Datenbank für die Tests
@pytest.fixture
def setup_database():
    test_db = 'test_database.db'
    repo = TaskRepository(db_path=test_db)

    # Datenbankverbindung und Tabelle erstellen
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            importance TEXT,
            urgency TEXT,
            fitness TEXT,
            status TEXT,
            completed_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

    yield repo

    # Entferne die Testdatenbank nach den Tests
    os.remove(test_db)


def test_save_task(setup_database):
    """
    Test the save_task method to ensure a task is saved correctly in the database.
    """
    repo = setup_database
    task = Task(
        title="Complete unit tests",
        due_date=date.today() + timedelta(days=3),
        importance=Priority.HIGH,
        urgency=Priority.LOW,
        fitness=Priority.HIGH,
        description="Write and verify unit tests for TaskRepository"
    )

    repo.save_task(task)
    tasks = repo.get_all_tasks()

    assert len(tasks) == 1
    assert tasks[0].title == "Complete unit tests"
    assert tasks[0].description == "Write and verify unit tests for TaskRepository"


def test_delete_task(setup_database):
    """
    Test the delete_task method to ensure a task is deleted from the database.
    """
    repo = setup_database
    task = Task(
        title="Delete test task",
        due_date=date.today() + timedelta(days=1),
        importance=Priority.LOW,
        urgency=Priority.HIGH,
        fitness=Priority.LOW
    )

    repo.save_task(task)
    tasks = repo.get_all_tasks()
    assert len(tasks) == 1  # Task wurde gespeichert

    task_id = tasks[0].id  # ID der gespeicherten Aufgabe
    repo.delete_task(task_id)
    tasks = repo.get_all_tasks()  # Nach Löschung erneut abrufen

    assert len(tasks) == 0  # Task wurde erfolgreich gelöscht


def test_get_all_tasks(setup_database):
    """
    Test the get_all_tasks method to retrieve tasks from the database.
    """
    repo = setup_database

    # Zwei Aufgaben speichern
    task1 = Task(title="Task 1", due_date=date.today(), importance=Priority.HIGH, urgency=Priority.HIGH,
                 fitness=Priority.HIGH)
    task2 = Task(title="Task 2", due_date=date.today(), importance=Priority.LOW, urgency=Priority.LOW,
                 fitness=Priority.LOW)

    repo.save_task(task1)
    repo.save_task(task2)
    tasks = repo.get_all_tasks()

    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"
