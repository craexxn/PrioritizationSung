import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
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
        self.archived_tasks = []  # Store archived tasks in memory
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
        Loads archived tasks for the current user from the database and updates the archived_listbox.
        """
        self.archived_listbox.delete(0, tk.END)
        self.archived_tasks = []  # Initialize the list to store Task objects
        conn = sqlite3.connect(self.controller.db_path)
        cursor = conn.cursor()

        try:
            # Fetch archived tasks for the current user
            cursor.execute('''
                SELECT title, description, due_date, importance, urgency, fitness, status, completed_date 
                FROM archived_tasks 
                WHERE user_id = ?
            ''', (self.controller.current_user_id,))
            rows = cursor.fetchall()

            for row in rows:
                title, description, due_date_str, importance_str, urgency_str, fitness_str, status_str, completed_date_str = row
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None
                importance = Priority[importance_str.upper()]
                urgency = Priority[urgency_str.upper()]
                fitness = Priority[fitness_str.upper()]
                status = Status[status_str.upper()] if status_str else Status.COMPLETED

                # Create a Task object and add it to the list
                task = Task(
                    title=title,
                    description=description,
                    due_date=due_date,
                    importance=importance,
                    urgency=urgency,
                    fitness=fitness,
                    status=status
                )
                self.archived_tasks.append(task)

                # Add a display-friendly version of the task to the listbox
                task_display = f"{title} - Due: {due_date_str if due_date_str else 'None'} - Status: {status_str} - Archived: {completed_date_str}"
                self.archived_listbox.insert(tk.END, task_display)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading archived tasks: {e}")
        finally:
            conn.close()

    def reactivate_task(self):
        """
        Reactivates the selected archived task and opens it in the TaskEditor for further editing.
        """
        selected_index = self.archived_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to reactivate.")
            return

        try:
            task_to_reactivate = self.archived_tasks[selected_index[0]]
            task_to_reactivate.status = Status.OPEN  # Set status to OPEN when reactivating

            # Add the task back to the main task list
            self.controller.tasks.append(task_to_reactivate)

            # Insert the task back into the "tasks" table
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (title, description, due_date, importance, urgency, fitness, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_to_reactivate.title,
                task_to_reactivate.description,
                task_to_reactivate.due_date.strftime('%Y-%m-%d') if task_to_reactivate.due_date else None,
                task_to_reactivate.importance.value,
                task_to_reactivate.urgency.value,
                task_to_reactivate.fitness.value,
                task_to_reactivate.status.value,
                self.controller.current_user_id
            ))

            # Remove the task from the "archived_tasks" table
            cursor.execute(
                'DELETE FROM archived_tasks WHERE title = ? AND user_id = ?',
                (task_to_reactivate.title, self.controller.current_user_id)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Task Reactivated", f"The task '{task_to_reactivate.title}' has been reactivated.")

            # Open the reactivated task in the TaskEditor
            TaskEditor(self.controller, "Edit Task", task=task_to_reactivate, index=len(self.controller.tasks) - 1)

            # Refresh the task list display
            self.controller.update_task_listbox()
            self.load_archived_tasks()  # Refresh the archive view
        except IndexError:
            messagebox.showerror("Error", "The selected task could not be found in the archive.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error reactivating task: {e}")



