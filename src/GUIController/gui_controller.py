import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ArchiveManager')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../NotificationManager')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../SettingsManager')))

from task import Task, Priority, Status
from archive_manager import ArchiveManager
from notification_manager import NotificationManager
from settings_manager import SettingsManager


class GUIController:
    """
    Controls the interaction between the GUI and the backend components.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")

        # Database path
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Database/database.db'))

        # Initialize managers
        self.settings_manager = SettingsManager(db_path=self.db_path)
        self.archive_manager = ArchiveManager(db_path=self.db_path)
        self.notification_manager = NotificationManager(self.settings_manager)

        # Create GUI elements
        self.create_widgets()

        # Initialize task list
        self.tasks = []
        self.load_tasks()

        # Schedule notifications
        self.schedule_notifications()

    def create_widgets(self):
        self.task_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=50, height=15)
        self.task_listbox.pack(pady=10)

        # Buttons for task actions
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Archive Task", command=self.archive_selected_task).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Show Archive", command=self.show_archive).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Settings", command=self.show_settings).grid(row=0, column=5, padx=5)

    def load_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        self.tasks.clear()

        cursor.execute('SELECT title, description, due_date, importance, urgency, fitness, status FROM tasks')
        rows = cursor.fetchall()

        for row in rows:
            title, description, due_date_str, importance_str, urgency_str, fitness_str, status_str = row
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            importance = Priority[importance_str.upper()]
            urgency = Priority[urgency_str.upper()]
            fitness = Priority[fitness_str.upper()]
            status = Status[status_str.upper()]

            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                importance=importance,
                urgency=urgency,
                fitness=fitness,
                status=status
            )
            self.tasks.append(task)

        conn.close()
        self.update_task_listbox()

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task.title)

    def add_task(self):
        TaskEditor(self, "Add New Task")

    def edit_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return
        selected_task = self.tasks[selected_index[0]]
        TaskEditor(self, "Edit Task", task=selected_task, index=selected_index[0])

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        del self.tasks[selected_index[0]]
        self.update_task_listbox()

    def archive_selected_task(self):
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to archive.")
            return
        task_to_archive = self.tasks[selected_index[0]]
        try:
            self.archive_manager.archive_task(task_to_archive)
            del self.tasks[selected_index[0]]
            self.update_task_listbox()
            messagebox.showinfo("Success", f"Task '{task_to_archive.title}' has been archived.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_archive(self):
        ArchiveViewer(self)

    def show_settings(self):
        SettingsWindow(self)

    def schedule_notifications(self):
        notifications = self.notification_manager.schedule_notifications(self.tasks)
        for notification in notifications:
            messagebox.showinfo("Notification", f"Task '{notification['task'].title}' is due on {notification['due_date']}.")

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
        self.geometry("400x400")

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

        # Save button
        tk.Button(self, text="Save", command=self.save_task).pack(pady=10)

    def save_task(self):
        """
        Saves the task and updates the controller's task list.
        """
        title = self.title_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        due_date_str = self.due_date_entry.get()

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in the format YYYY-MM-DD.")
            return

        # Convert dropdown values to uppercase to match the Priority Enum
        importance = Priority[self.importance_var.get().upper()]
        urgency = Priority[self.urgency_var.get().upper()]
        fitness = Priority[self.fitness_var.get().upper()]

        if self.task:
            # Update the existing task
            self.task.title = title
            self.task.description = description
            self.task.due_date = due_date
            self.task.importance = importance
            self.task.urgency = urgency
            self.task.fitness = fitness
            self.controller.tasks[self.index] = self.task
        else:
            # Create a new task
            new_task = Task(title=title, description=description, due_date=due_date, importance=importance,
                            urgency=urgency, fitness=fitness)
            self.controller.tasks.append(new_task)

        self.controller.update_task_listbox()
        self.destroy()

class SettingsWindow(tk.Toplevel):
    """
    A window for managing application settings.
    """

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.settings_manager = controller.settings_manager
        self.title("Settings")
        self.geometry("300x250")
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        """
        Creates widgets for the settings window.
        """
        tk.Label(self, text="Notification Interval (days):").pack(pady=5)
        self.notification_interval_var = tk.IntVar()
        self.notification_interval_entry = tk.Entry(self, textvariable=self.notification_interval_var)
        self.notification_interval_entry.pack(pady=5)

        self.notifications_enabled_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Enable Notifications", variable=self.notifications_enabled_var).pack(pady=5)

        tk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=10)

    def load_settings(self):
        """
        Loads the current settings and populates the UI fields.
        """
        settings = self.settings_manager.get_settings()
        self.notification_interval_var.set(settings.get("notification_interval", 1))
        self.notifications_enabled_var.set(settings.get("notifications_enabled", True))

    def save_settings(self):
        """
        Saves the settings entered by the user.
        """
        notification_interval = self.notification_interval_var.get()
        notifications_enabled = self.notifications_enabled_var.get()

        # Save settings using the SettingsManager
        self.settings_manager.save_settings(
            notification_interval=notification_interval,
            auto_archive=True,  # Assuming default or predefined settings
            auto_delete=False,   # Assuming default or predefined settings
            notifications_enabled=notifications_enabled,
            default_priorities={"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}  # Replace with actual values if needed
        )

        messagebox.showinfo("Settings Saved", "Your settings have been saved.")
        self.destroy()
