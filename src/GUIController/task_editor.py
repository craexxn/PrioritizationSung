import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))

from task import Task, Priority, Status


class TaskEditor(tk.Toplevel):
    """
    Window for adding, editing, or updating a task's status.
    """

    def __init__(self, controller, title, task=None, index=None):
        super().__init__(controller.root)
        self.controller = controller
        self.task = task
        self.index = index
        self.title(title)
        self.geometry("400x600")

        # Fields for task details
        tk.Label(self, text="Title:").pack(pady=5)
        self.title_entry = tk.Entry(self, width=50)
        self.title_entry.pack(pady=5)
        if task:
            self.title_entry.insert(0, task.title)

        tk.Label(self, text="Description:").pack(pady=5)
        self.description_text = tk.Text(self, width=50, height=5)
        self.description_text.pack(pady=5)
        if task:
            self.description_text.insert(tk.END, task.description)

        tk.Label(self, text="Due Date (YYYY-MM-DD):").pack(pady=5)
        self.due_date_entry = tk.Entry(self, width=50)
        self.due_date_entry.pack(pady=5)
        if task and task.due_date:
            self.due_date_entry.insert(0, task.due_date.strftime("%Y-%m-%d"))

        # Dropdowns for priority levels
        tk.Label(self, text="Importance:").pack(pady=5)
        self.importance_var = tk.StringVar(value="Select Priority")
        self.importance_combo = ttk.Combobox(self, textvariable=self.importance_var, values=[p.value for p in Priority], state="readonly")
        self.importance_combo.pack(pady=5)
        if task:
            self.importance_combo.set(task.importance.value)

        tk.Label(self, text="Urgency:").pack(pady=5)
        self.urgency_var = tk.StringVar(value="Select Priority")
        self.urgency_combo = ttk.Combobox(self, textvariable=self.urgency_var, values=[p.value for p in Priority], state="readonly")
        self.urgency_combo.pack(pady=5)
        if task:
            self.urgency_combo.set(task.urgency.value)

        tk.Label(self, text="Fitness:").pack(pady=5)
        self.fitness_var = tk.StringVar(value="Select Priority")
        self.fitness_combo = ttk.Combobox(self, textvariable=self.fitness_var, values=[p.value for p in Priority], state="readonly")
        self.fitness_combo.pack(pady=5)
        if task:
            self.fitness_combo.set(task.fitness.value)

        # Buttons
        tk.Button(self, text="Save", command=self.save_task).pack(pady=10)
        if self.task and self.task.status == Status.COMPLETED:
            tk.Button(self, text="Mark as Open", command=self.mark_task_open).pack(pady=5)  # New Button

    def save_task(self):
        """
        Saves the task to the database.
        """
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        due_date_str = self.due_date_entry.get().strip()
        user_id = self.controller.current_user_id

        # Validate input
        if not title:
            messagebox.showerror("Error", "Title is required.")
            return

        if self.importance_var.get() == "Select Priority" or self.urgency_var.get() == "Select Priority" or self.fitness_var.get() == "Select Priority":
            messagebox.showerror("Error", "All priority levels must be selected.")
            return

        # Parse due_date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Error", "Invalid due date format. Use YYYY-MM-DD.")
                return

        # Convert dropdown values to Priority Enum
        importance = Priority[self.importance_var.get().upper()]
        urgency = Priority[self.urgency_var.get().upper()]
        fitness = Priority[self.fitness_var.get().upper()]
        status = self.task.status if self.task else Status.OPEN

        conn = sqlite3.connect(self.controller.db_path)
        cursor = conn.cursor()

        if self.task:
            # Update existing task
            cursor.execute('''
                UPDATE tasks
                SET title = ?, description = ?, due_date = ?, importance = ?, urgency = ?, fitness = ?, status = ?
                WHERE id = ?
            ''', (title, description, due_date, importance.value, urgency.value, fitness.value, status.value, self.task.id))
        else:
            # Insert new task
            cursor.execute('''
                INSERT INTO tasks (title, description, due_date, importance, urgency, fitness, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, due_date, importance.value, urgency.value, fitness.value, status.value, user_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Task saved successfully.")
        self.controller.load_tasks()  # Refresh the task list
        self.destroy()  # Close the editor window

    @staticmethod
    def mark_task_open(task, controller):
        """
        Marks the given task as open and updates the database.
        """
        try:
            conn = sqlite3.connect(controller.db_path)
            cursor = conn.cursor()

            # Update the task's status in the database
            cursor.execute('''
                UPDATE tasks
                SET status = ?
                WHERE id = ?
            ''', (Status.OPEN.value, task.id))
            conn.commit()
            conn.close()

            # Update the task's status in the task list
            task.status = Status.OPEN
            messagebox.showinfo("Success", f"Task '{task.title}' marked as open.")
            controller.load_tasks()  # Reload the task list
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error marking task as open: {e}")
