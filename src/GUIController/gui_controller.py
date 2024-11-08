import os
import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ArchiveManager')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../NotificationManager')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../SettingsManager')))

from task import Task, Priority, Status
from archive_manager import ArchiveManager
from notification_manager import NotificationManager
from settings_manager import SettingsManager
from task_editor import TaskEditor
from settings_window import SettingsWindow


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
