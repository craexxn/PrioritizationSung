import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))
from task import Task, Priority

class TaskEditor(tk.Toplevel):
    """
    Window for adding or editing a task.
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
        self.importance_var = tk.StringVar(value="HIGH")
        self.importance_combo = ttk.Combobox(self, textvariable=self.importance_var, values=[p.value for p in Priority], state="readonly")
        self.importance_combo.pack(pady=5)
        if task:
            self.importance_combo.set(task.importance.value)

        tk.Label(self, text="Urgency:").pack(pady=5)
        self.urgency_var = tk.StringVar(value="LOW")
        self.urgency_combo = ttk.Combobox(self, textvariable=self.urgency_var, values=[p.value for p in Priority], state="readonly")
        self.urgency_combo.pack(pady=5)
        if task:
            self.urgency_combo.set(task.urgency.value)

        tk.Label(self, text="Fitness:").pack(pady=5)
        self.fitness_var = tk.StringVar(value="LOW")
        self.fitness_combo = ttk.Combobox(self, textvariable=self.fitness_var, values=[p.value for p in Priority], state="readonly")
        self.fitness_combo.pack(pady=5)
        if task:
            self.fitness_combo.set(task.fitness.value)

        tk.Button(self, text="Save", command=self.save_task).pack(pady=10)

    def save_task(self):
        title = self.title_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        due_date_str = self.due_date_entry.get()

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in the format YYYY-MM-DD.")
            return

        # Check if due date is in the past
        if due_date < datetime.today().date():
            messagebox.showerror("Invalid Due Date", "The due date cannot be in the past. Please select a future date.")
            return

        # Convert dropdown values to match the Priority Enum
        importance = Priority[self.importance_var.get().upper()]
        urgency = Priority[self.urgency_var.get().upper()]
        fitness = Priority[self.fitness_var.get().upper()]

        # Update existing task if editing
        if self.task:
            self.task.title = title
            self.task.description = description
            self.task.due_date = due_date
            self.task.importance = importance
            self.task.urgency = urgency
            self.task.fitness = fitness

            if self.index is not None:
                self.controller.tasks[self.index] = self.task
        else:
            new_task = Task(
                title=title,
                description=description,
                due_date=due_date,
                importance=importance,
                urgency=urgency,
                fitness=fitness
            )
            self.controller.tasks.append(new_task)

        self.controller.update_task_listbox()
        self.destroy()
