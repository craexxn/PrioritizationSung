import sqlite3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Task')))

from task import Task, Priority, Status
from datetime import date


class TaskRepository:
    """
    TaskRepository handles database operations for tasks.
    """

    def __init__(self, db_path='database.db'):
        """
        Initializes the TaskRepository with a path to the SQLite database.

        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path

    def save_task(self, task: Task):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tasks (title, description, due_date, importance, urgency, fitness, status, completed_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.title,
            task.description,
            task.due_date.isoformat() if task.due_date else None,
            task.importance.value,
            task.urgency.value,
            task.fitness.value,
            task.status.value,
            task.completed_date.isoformat() if task.completed_date else None
        ))

        # Set the ID of the task instance to the last row ID
        task.id = cursor.lastrowid
        print(f"Saved task with ID: {task.id}")  # Debug-Ausgabe

        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        """
        Deletes a task from the database based on its ID.

        :param task_id: ID of the task to delete.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

        conn.commit()
        conn.close()

    def get_all_tasks(self):
        """
        Retrieves all tasks from the database.

        :return: List of Task instances.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tasks')
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            task = Task(
                title=row[1],
                description=row[2],
                due_date=date.fromisoformat(row[3]) if row[3] else None,
                importance=Priority(row[4]),
                urgency=Priority(row[5]),
                fitness=Priority(row[6]),
                task_id=row[0]  # Die ID der Aufgabe setzen
            )
            task.status = Status(row[7])
            task.completed_date = date.fromisoformat(row[8]) if row[8] else None
            tasks.append(task)

        conn.close()
        return tasks
