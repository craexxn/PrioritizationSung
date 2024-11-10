import os
import sys
import math
import sqlite3
import tkinter as tk
from tkinter import messagebox, Canvas
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
        self.root.title("Sung Task Manager")

        # Database path
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Database/database.db'))

        # Initialize managers
        self.settings_manager = SettingsManager(db_path=self.db_path)
        self.archive_manager = ArchiveManager(db_path=self.db_path)
        self.notification_manager = NotificationManager(self.settings_manager)

        # Track the currently selected task for editing
        self.selected_task = None  # New attribute to keep track of the selected task

        # Create GUI elements
        self.create_widgets()

        # Initialize task list
        self.tasks = []
        self.load_tasks()
        self.initialize_priority_combinations()  # For testing

        # Schedule notifications
        self.schedule_notifications()

    def create_widgets(self):
        # Main canvas for the Venn Diagram
        self.venn_canvas = Canvas(self.root, width=1024, height=1024)
        self.venn_canvas.pack(pady=10)

        # Draw Venn diagram areas with overlapping regions
        self.draw_venn_diagram()

        # Create "LOW Priority Tasks" listbox on the right side
        self.low_listbox_label = tk.Label(self.root, text="LOW Priority Tasks", font=("Helvetica", 12, "bold"))
        self.low_listbox_label.place(x=850, y=50)
        self.low_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=25, height=20)
        self.low_listbox.place(x=850, y=80)

        # Bind selection event for low_listbox to update selected task index
        self.low_listbox.bind("<<ListboxSelect>>", self.low_listbox_select)

       # Buttons for task actions
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Archive Task", command=self.archive_selected_task).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Show Archive", command=self.show_archive).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Settings", command=self.show_settings).grid(row=0, column=5, padx=5)

    def draw_venn_diagram(self):
        """
        Draws a Venn diagram on the canvas to represent the priority areas, centered in a 1024x1024 window.
        Enlarges the circles to fill more space, with overlapping transparency effects.
        """

        # Center of the canvas
        center_x, center_y = 512, 512
        medium_radius = 275  # Adjusted radius for each circle to avoid overlap with "LOW Priority Tasks"

        # Colors with transparency
        importance_color = "#add8e6"  # Light blue for Importance
        fitness_color = "#90ee90"  # Light green for Fitness
        urgency_color = "#ffd700"  # Light yellow for Urgency

        # Draw circles for Importance, Urgency, and Fitness
        self.venn_canvas.create_oval(center_x - medium_radius - 150, center_y - medium_radius,
                                     center_x + medium_radius - 150, center_y + medium_radius,
                                     fill=importance_color, outline="", tags="importance_area")
        self.venn_canvas.create_text(center_x - 150, center_y - medium_radius - 20, text="IMPORTANT: Plan", fill="blue",
                                     font=("Helvetica", 14, "bold"))

        self.venn_canvas.create_oval(center_x - medium_radius + 150, center_y - medium_radius,
                                     center_x + medium_radius + 150, center_y + medium_radius,
                                     fill=fitness_color, outline="", tags="fitness_area")
        self.venn_canvas.create_text(center_x + 150, center_y - medium_radius - 20, text="FITNESS: Make Time", fill="green",
                                     font=("Helvetica", 14, "bold"))

        self.venn_canvas.create_oval(center_x - medium_radius, center_y - medium_radius + 150,
                                     center_x + medium_radius, center_y + medium_radius + 150,
                                     fill=urgency_color, outline="", tags="urgency_area")
        self.venn_canvas.create_text(center_x, center_y + medium_radius + 30, text="URGENT: Delegate Next", fill="red",
                                     font=("Helvetica", 14, "bold"))

        # Text labels for Do Now section, adjusted to match new circle positions
        self.venn_canvas.create_text(center_x, center_y + 100, text="Do Now", fill="black", font=("Helvetica", 16, "bold"))

        # Add a "LOW" priority listbox on the right side of the window
        self.low_listbox_label = tk.Label(self.root, text="LOW Priority Tasks", font=("Helvetica", 12, "bold"))
        self.low_listbox_label.place(x=850, y=50)

        self.low_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=25, height=20)
        self.low_listbox.place(x=850, y=80)

    def load_tasks(self):
        """
        Loads tasks from the database and updates the task display on the Venn diagram.
        """
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
        self.update_task_venn_diagram()

    def initialize_priority_combinations(self):
        """
        Initializes tasks with all possible priority combinations (HHH, HHL, HLH, etc.)
        and displays them on the Venn diagram for visualization purposes.
        """
        combinations = [
            ("HHH", Priority.HIGH, Priority.HIGH, Priority.HIGH),
            ("HHL", Priority.HIGH, Priority.HIGH, Priority.LOW),
            ("HLH", Priority.HIGH, Priority.LOW, Priority.HIGH),
            ("LHH", Priority.LOW, Priority.HIGH, Priority.HIGH),
            ("LLH", Priority.LOW, Priority.LOW, Priority.HIGH),
            ("LHL", Priority.LOW, Priority.HIGH, Priority.LOW),
            ("HLL", Priority.HIGH, Priority.LOW, Priority.LOW),
            ("LLL", Priority.LOW, Priority.LOW, Priority.LOW)
        ]

        # Clear existing tasks in case you don't want to mix these with real tasks
        self.tasks.clear()

        # Create a task for each combination and add it to the tasks list
        for name, importance, urgency, fitness in combinations:
            task = Task(
                title=name,
                description=f"Task with priority {name}",
                due_date=datetime.today().date(),
                importance=importance,
                urgency=urgency,
                fitness=fitness
            )
            self.tasks.append(task)

        # Refresh the Venn Diagram display with the initialized tasks
        self.update_task_venn_diagram()

    def update_task_venn_diagram(self):
        """
        Updates the Venn diagram display with the current tasks.
        Tasks are positioned based on priority levels:
        - Only one HIGH: positioned at the edge of the relevant priority circle.
        - Two HIGHs: positioned at the edge of the overlap region of the two relevant circles.
        - Three HIGHs: positioned in the center around "Do Now".
        """
        self.venn_canvas.delete("task_text")

        venn_center_x, venn_center_y = 512, 512
        medium_radius = 275
        outer_radius_offset = 1
        overlap_radius_offset = 1
        high_high_high_radius = 75

        importance_center = (venn_center_x - medium_radius, venn_center_y + medium_radius)
        urgency_center = (venn_center_x, venn_center_y - medium_radius)
        fitness_center = (venn_center_x + medium_radius, venn_center_y + medium_radius)

        high_high_high_counter = 0
        high_high_high_angle_step = 45

        for task in self.tasks:
            if task.importance == Priority.HIGH and task.urgency == Priority.HIGH and task.fitness == Priority.HIGH:
                angle_rad = math.radians(high_high_high_angle_step * high_high_high_counter)
                x = venn_center_x + high_high_high_radius * math.cos(angle_rad)
                y = venn_center_y + 100 + high_high_high_radius * math.sin(angle_rad)
                high_high_high_counter += 1
            elif task.importance == Priority.HIGH and task.urgency == Priority.HIGH:
                x = int((importance_center[0] + urgency_center[0]) / 2 * overlap_radius_offset)
                y = int((importance_center[1] + urgency_center[1]) / 2.1 * overlap_radius_offset)
            elif task.importance == Priority.HIGH and task.fitness == Priority.HIGH:
                x = int((importance_center[0] + fitness_center[0]) / 2 * overlap_radius_offset)
                y = int((importance_center[1] + fitness_center[1]) / 2.1 * overlap_radius_offset)
            elif task.urgency == Priority.HIGH and task.fitness == Priority.HIGH:
                x = int((urgency_center[0] + fitness_center[0]) / 2 * overlap_radius_offset)
                y = int((urgency_center[1] + fitness_center[1]) / 2.1 * overlap_radius_offset)
            elif task.importance == Priority.HIGH:
                x = int(importance_center[0] * outer_radius_offset)
                y = int(importance_center[1] * outer_radius_offset / 2)
            elif task.urgency == Priority.HIGH:
                x = int(urgency_center[0] * outer_radius_offset)
                y = int(urgency_center[1] * outer_radius_offset * 3.7)
            elif task.fitness == Priority.HIGH:
                x = int(fitness_center[0] * outer_radius_offset)
                y = int(fitness_center[1] * outer_radius_offset / 2)
            else:
                self.low_listbox.insert(tk.END, task.title)
                continue

            # Create the task text label with a unique tag based on task title
            text_id = self.venn_canvas.create_text(x, y, text=task.title, tags=("task_text", task.title))
            # Bind a click event to the task label
            self.venn_canvas.tag_bind(text_id, "<Button-1>", lambda event, task=task, text_id=text_id: self.select_task(event, task, text_id))

    def select_task(self, event, task, text_id):
        """
        Marks the task as selected and highlights it.
        """
        # Deselect the previously selected task, if any
        if self.selected_task is not None:
            self.venn_canvas.itemconfig(self.selected_task["text_id"], fill="black")

        # Set the new selected task and change its color to indicate selection
        self.selected_task = {"task": task, "text_id": text_id}
        self.venn_canvas.itemconfig(text_id, fill="red")  # Highlight selected task in red

    def edit_task_from_canvas(self, task):
        """
        Opens the TaskEditor for the specified task when clicked on the Venn diagram.
        """
        TaskEditor(self, "Edit Task", task=task)

    def task_listbox_select(self, event):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            self.selected_task_index = selected_index[0]
            # Clear selection in the LOW listbox
            self.low_listbox.selection_clear(0, tk.END)
        else:
            self.selected_task_index = None

    def update_task_listbox(self):
        """
        Refreshes the Venn diagram with the current list of tasks.
        """
        self.update_task_venn_diagram()
        self.low_listbox.delete(0, tk.END)
        for task in self.tasks:
            if task.importance == Priority.LOW and task.urgency == Priority.LOW and task.fitness == Priority.LOW:
                self.low_listbox.insert(tk.END, task.title)

    def low_listbox_select(self, event):
        selected_index = self.low_listbox.curselection()
        if not selected_index:
            return

        selected_title = self.low_listbox.get(selected_index)
        selected_task = next((task for task in self.tasks if task.title == selected_title), None)

        if selected_task:
            self.selected_task_index = self.tasks.index(selected_task)
            # Clear selection in the Venn diagram
            self.task_listbox.selection_clear(0, tk.END)
        else:
            self.selected_task_index = None

    def add_task(self):
        TaskEditor(self, "Add New Task")

    def edit_task(self):
        if hasattr(self, "selected_task_index") and self.selected_task_index is not None:
            selected_task = self.tasks[self.selected_task_index]
            TaskEditor(self, "Edit Task", task=selected_task, index=self.selected_task_index)
        else:
            messagebox.showwarning("No Selection", "Please select a task to edit.")

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
