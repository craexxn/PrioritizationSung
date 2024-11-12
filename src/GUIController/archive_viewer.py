import os
import sys
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))

from task import Task, Priority, Status
from task_editor import TaskEditor  # Import TaskEditor to use for reactivation


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

        # Reactivate and Close buttons
        tk.Button(self, text="Reactivate Task", command=self.reactivate_task).pack(pady=5)
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

    def reactivate_task(self):
        """
        Reactivates the selected archived task and opens it in the TaskEditor for further editing.
        """
        selected_index = self.archived_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to reactivate.")
            return

        selected_task_title = self.archived_listbox.get(selected_index).split(" - ")[0]

        # Fetch the task details from the archive
        conn = sqlite3.connect(self.controller.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT title, description, due_date, importance, urgency, fitness, status FROM archived_tasks WHERE title = ?',
            (selected_task_title,))
        task_data = cursor.fetchone()

        if task_data:
            title, description, due_date_str, importance_str, urgency_str, fitness_str, status_str = task_data
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            importance = Priority[importance_str.upper()]
            urgency = Priority[urgency_str.upper()]
            fitness = Priority[fitness_str.upper()]
            status = Status.OPEN  # Set status to open when reactivating

            # Create a new Task object and add it back to the main task list
            reactivated_task = Task(
                title=title,
                description=description,
                due_date=due_date,
                importance=importance,
                urgency=urgency,
                fitness=fitness,
                status=status
            )

            self.controller.tasks.append(reactivated_task)
            self.controller.update_task_listbox()

            # Delete the task from the archived_tasks table
            cursor.execute('DELETE FROM archived_tasks WHERE title = ?', (title,))
            conn.commit()  # Commit changes to the database
            messagebox.showinfo("Task Reactivated", f"The task '{title}' has been reactivated.")

            # Open the reactivated task in the TaskEditor
            TaskEditor(self.controller, "Edit Task", task=reactivated_task, index=len(self.controller.tasks) - 1)

        # Close the database connection after all operations are complete
        conn.close()

