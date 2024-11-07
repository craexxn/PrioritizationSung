import os
import sys
import sqlite3
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))

from task import Task, Status, Priority


class ArchiveManager:
    """
    Manages the archiving and deletion of completed tasks in the SQLite database.
    This class handles completed tasks' storage and automatic deletion after a specified period.
    """

    def __init__(self, db_path):
        """
        Initializes the ArchiveManager with the path to the SQLite database.

        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._create_archived_tasks_table()

    def _create_archived_tasks_table(self):
        """
        Creates the archived_tasks table in the database if it does not exist.
        This table stores completed tasks that are moved from the main tasks list.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archived_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                importance TEXT CHECK(importance IN ('Low', 'High')),
                urgency TEXT CHECK(urgency IN ('Low', 'High')),
                fitness TEXT CHECK(fitness IN ('Low', 'High')),
                status TEXT CHECK(status IN ('Open', 'In Progress', 'Completed')),
                completed_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def archive_task(self, task):
        """
        Archives a completed task by inserting it into the archived_tasks table.

        :param task: Task object to be archived.
        :raises ValueError: If the task is not completed.
        """
        if task.status != Status.COMPLETED:
            raise ValueError("Only completed tasks can be archived.")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO archived_tasks (title, description, due_date, importance, urgency, fitness, status, completed_date)
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
        conn.commit()
        conn.close()

    def auto_archive_task(self, task, days_until_archive):
        """
        Automatically archives a task if it has been completed for a specified number of days.

        :param task: Task object to be considered for archiving.
        :param days_until_archive: Number of days after completion to wait before archiving.
        """
        if task.status == Status.COMPLETED and task.completed_date:
            days_completed = (date.today() - task.completed_date).days
            if days_completed >= days_until_archive:
                self.archive_task(task)

    def auto_delete_task(self, task, days_until_delete):
        """
        Automatically deletes an archived task if it has been in the archive for a specified number of days.

        :param task: Task object to be considered for deletion.
        :param days_until_delete: Number of days after archiving to wait before deletion.
        """
        if task.completed_date:
            days_archived = (date.today() - task.completed_date).days
            if days_archived >= days_until_delete:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM archived_tasks WHERE id = ?', (task.id,))
                conn.commit()
                conn.close()