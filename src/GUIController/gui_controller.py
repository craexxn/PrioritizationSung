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
        # # Main canvas for the Venn Diagram
        self.venn_canvas = Canvas(self.root, width=1024, height=1024)
        self.venn_canvas.pack(pady=(50, 10))  # Add space above canvas for button frame

        # Draw Venn diagram areas with overlapping regions
        self.draw_venn_diagram()

        # Create "LOW Priority Tasks" listbox on the right side
        self.low_listbox_label = tk.Label(self.root, text="LOW Priority Tasks", font=("Helvetica", 12, "bold"))
        self.low_listbox_label.place(x=850, y=50)
        self.low_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=25, height=20)
        self.low_listbox.place(x=850, y=80)

        # Bind selection event for low_listbox to update selected task index
        self.low_listbox.bind("<<ListboxSelect>>", self.low_listbox_select)

        # Buttons for task actions at the top of the window
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side="top", pady=5)  # Position the button frame at the top

        # Create buttons for task actions
        tk.Button(btn_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Mark as Completed", command=self.mark_task_completed).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Archive Task", command=self.archive_selected_task).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Show Archive", command=self.show_archive).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Settings", command=self.show_settings).grid(row=0, column=6, padx=5)


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
        Updates the Venn diagram display with the current tasks, adding slight offsets for overlapping tasks.
        Tasks with the same position are arranged in a circular pattern to avoid overlap.
        """
        self.venn_canvas.delete("task_text")

        venn_center_x, venn_center_y = 512, 512
        medium_radius = 275
        offset_radius = 15  # Radius for offset circle around each position for overlapping tasks
        high_high_high_radius = 75  # Radius for the central "Do Now" region

        # Centers for each priority circle
        importance_center = (venn_center_x - medium_radius, venn_center_y)
        urgency_center = (venn_center_x, venn_center_y + medium_radius)
        fitness_center = (venn_center_x + medium_radius, venn_center_y)

        # Dictionary to track tasks at each position
        position_count = {}

        for task in self.tasks:
            # Determine position based on priorities
            if task.importance == Priority.HIGH and task.urgency == Priority.HIGH and task.fitness == Priority.HIGH:
                # Place tasks with HHH priority in a circular pattern around "Do Now"
                if "HHH" not in position_count:
                    position_count["HHH"] = []
                position_count["HHH"].append(task)
            else:
                # Calculate position for other combinations of priorities
                if task.importance == Priority.HIGH and task.urgency == Priority.HIGH:
                    position = (
                    (importance_center[0] + urgency_center[0]) / 2, (importance_center[1] + urgency_center[1]) / 2)
                elif task.importance == Priority.HIGH and task.fitness == Priority.HIGH:
                    position = (
                    (importance_center[0] + fitness_center[0]) / 2, (importance_center[1] + fitness_center[1]) / 2)
                elif task.urgency == Priority.HIGH and task.fitness == Priority.HIGH:
                    position = (
                    (urgency_center[0] + fitness_center[0]) / 2, (urgency_center[1] + fitness_center[1]) / 2)
                elif task.importance == Priority.HIGH:
                    position = importance_center
                elif task.urgency == Priority.HIGH:
                    position = urgency_center
                elif task.fitness == Priority.HIGH:
                    position = fitness_center
                else:
                    # For tasks with all LOWs, add to the "LOW Priority Tasks" list
                    self.low_listbox.insert(tk.END, task.title)
                    continue

                # Track tasks at this calculated position
                if position not in position_count:
                    position_count[position] = []
                position_count[position].append(task)

        # Display tasks at each position, applying offsets for overlapping tasks
        for position, tasks in position_count.items():
            if position == "HHH":
                # Arrange HHH tasks in a circular pattern around "Do Now"
                angle_step = 360 / len(tasks)
                for i, task in enumerate(tasks):
                    angle_rad = math.radians(i * angle_step)
                    x = venn_center_x + high_high_high_radius * math.cos(angle_rad)
                    y = venn_center_y + 100 + high_high_high_radius * math.sin(angle_rad)  # 100 is offset for "Do Now"
                    text_id = self.venn_canvas.create_text(x, y, text=task.title, tags="task_text")
                    self.venn_canvas.tag_bind(text_id, "<Button-1>",
                                              lambda e, t=task, tid=text_id: self.select_task(e, t, tid))
            else:
                # Arrange tasks with same position in a small circular pattern around the position
                angle_step = 360 / len(tasks)
                for i, task in enumerate(tasks):
                    angle_rad = math.radians(i * angle_step)
                    x_offset = position[0] + offset_radius * math.cos(angle_rad)
                    y_offset = position[1] + offset_radius * math.sin(angle_rad)
                    text_id = self.venn_canvas.create_text(x_offset, y_offset, text=task.title, tags="task_text")
                    self.venn_canvas.tag_bind(text_id, "<Button-1>",
                                              lambda e, t=task, tid=text_id: self.select_task(e, t, tid))

    def select_task(self, event, task, text_id):
        """
        Marks the task as selected and highlights it for editing.
        """
        # Deselect the previously selected task, if any
        if self.selected_task is not None:
            self.venn_canvas.itemconfig(self.selected_task["text_id"], fill="black")

        # Set the new selected task and change its color to indicate selection
        self.selected_task = {"task": task, "text_id": text_id}
        self.venn_canvas.itemconfig(text_id, fill="red")  # Highlight selected task in red

        # Find and store the index of the selected task
        self.selected_task_index = self.tasks.index(task)

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
        if self.selected_task_index is None:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return
        selected_task = self.tasks[self.selected_task_index]
        TaskEditor(self, "Edit Task", task=selected_task, index=self.selected_task_index)

    def delete_task(self):
        """
        Deletes the selected task from the list and updates the diagram and listbox accordingly.
        """
        # If a task is selected in the Venn diagram
        if self.selected_task:
            task_to_delete = self.selected_task["task"]
            self.tasks.remove(task_to_delete)
            self.venn_canvas.delete(self.selected_task["text_id"])  # Remove the element from the diagram
            self.selected_task = None  # Reset the selected task

        # If a task is selected in the "LOW" listbox
        elif self.low_listbox.curselection():
            selected_index = self.low_listbox.curselection()[0]
            selected_task_title = self.low_listbox.get(selected_index)
            task_to_delete = next((task for task in self.tasks if task.title == selected_task_title), None)
            if task_to_delete:
                self.tasks.remove(task_to_delete)
                self.low_listbox.delete(selected_index)  # Remove the element from the "LOW" listbox

        else:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        self.update_task_listbox()  # Refresh the diagram and list

    def mark_task_completed(self):
        """
        Marks the selected task as completed.
        """
        if self.selected_task_index is None:
            messagebox.showwarning("No Selection", "Please select a task to mark as completed.")
            return
        selected_task = self.tasks[self.selected_task_index]
        selected_task.status = Status.COMPLETED
        messagebox.showinfo("Task Completed", f"Task '{selected_task.title}' has been marked as completed.")
        self.update_task_listbox()

    def archive_selected_task(self):
        """
        Archives the selected task and updates the diagram and listbox accordingly.
        """
        # Check if a task is selected in the Venn diagram
        if self.selected_task:
            task_to_archive = self.selected_task["task"]
            try:
                # Archive the task
                self.archive_manager.archive_task(task_to_archive)
                # Remove the task from the main task list and Venn diagram
                self.tasks.remove(task_to_archive)
                self.venn_canvas.delete(self.selected_task["text_id"])  # Remove from diagram
                self.selected_task = None  # Clear selection
                messagebox.showinfo("Success", f"Task '{task_to_archive.title}' has been archived.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        # Check if a task is selected in the "LOW Priority Tasks" listbox
        elif self.low_listbox.curselection():
            selected_index = self.low_listbox.curselection()[0]
            selected_task_title = self.low_listbox.get(selected_index)
            task_to_archive = next((task for task in self.tasks if task.title == selected_task_title), None)
            if task_to_archive:
                try:
                    # Archive the task
                    self.archive_manager.archive_task(task_to_archive)
                    # Remove the task from the main task list and listbox
                    self.tasks.remove(task_to_archive)
                    self.low_listbox.delete(selected_index)  # Remove from "LOW" listbox
                    messagebox.showinfo("Success", f"Task '{task_to_archive.title}' has been archived.")
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("No Selection", "Please select a task to archive.")
            return

        # Refresh the task display
        self.update_task_listbox()

    def show_archive(self):
        ArchiveViewer(self)

    def show_settings(self):
        SettingsWindow(self)

    def schedule_notifications(self):
        notifications = self.notification_manager.schedule_notifications(self.tasks)
        for notification in notifications:
            messagebox.showinfo("Notification", f"Task '{notification['task'].title}' is due on {notification['due_date']}.")
