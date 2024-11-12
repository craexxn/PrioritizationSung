import os
import sys
import tkinter as tk
from tkinter import messagebox
import sqlite3

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))

from task import Task, Priority, Status

class ArchiveViewer(tk.Toplevel):
    """
    A window for viewing archived tasks.
    """

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.title("Archived Tasks")
        self.geometry("400x300")
        self.archive_manager = controller.archive_manager
        self.create_widgets()
        self.load_archived_tasks()

    def create_widgets(self):
        """
        Creates widgets for displaying archived tasks.
        """
        self.archived_listbox = tk.Listbox(self, width=50, height=15)
        self.archived_listbox.pack(pady=10)
        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)

    def load_archived_tasks(self):
        """
        Loads archived tasks from the database.
        """
        self.archived_listbox.delete(0, tk.END)
        conn = sqlite3.connect(self.controller.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT title, description, due_date, importance, urgency, fitness, status FROM archived_tasks')
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            title, description, due_date_str, importance_str, urgency_str, fitness_str, status_str = row
            task_text = f"{title} - {due_date_str} - {status_str}"
            self.archived_listbox.insert(tk.END, task_text)
