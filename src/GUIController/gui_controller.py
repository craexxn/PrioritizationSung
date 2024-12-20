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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../FilterController')))


from task import Task, Priority, Status
from archive_manager import ArchiveManager
from notification_manager import NotificationManager
from settings_manager import SettingsManager
from task_editor import TaskEditor
from settings_window import SettingsWindow
from archive_viewer import ArchiveViewer
from login_window import LoginWindow
from filter_controller import FilterController
from drag_drop import DragDropHandler



class GUIController:
    """
    Controls the interaction between the GUI and the backend components.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Sung Task Manager")

        self.current_user = None  # Stores the logged-in user's name

        if getattr(sys, 'frozen', False):  # Executable mode
            db_path = os.path.join(os.path.dirname(sys.executable), "database.db")
        else:  # Script mode
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Database/database.db'))

        self.db_path = db_path

        self.login_window = LoginWindow(self)

        # Initialize the task list and canvas mappings
        self.tasks = []  # Holds all tasks
        self.task_elements = {}  # Maps task titles to their canvas elements for drag-and-drop

        self.settings_manager = SettingsManager(db_path=self.db_path)
        self.archive_manager = ArchiveManager(db_path=self.db_path)
        self.notification_manager = NotificationManager(self.settings_manager)

        self.drag_drop_handler = None  # Drag-and-drop handler, initialized later

        self.selected_task = None  # Tracks selected task for editing
        self.selected_task_index = None  # index of selected task

        self.create_widgets()

        if self.current_user:
            self.load_tasks()

        self.schedule_notifications()
        self.filter_controller = FilterController(self)

    def create_widgets(self):

        # Main canvas for the Venn Diagram
        self.venn_canvas = Canvas(self.root, width=1024, height=1024)
        self.venn_canvas.pack(pady=0)  # Add space above canvas for button frame

        # Draw Venn diagram areas with overlapping regions
        self.draw_venn_diagram()

        # Create "LOW Priority Tasks" listbox on the right side
        self.low_listbox_label = tk.Label(self.root, text="LOW Priority Tasks", font=("Helvetica", 12, "bold"))
        self.low_listbox_label.place(relx=1.0, rely=0.05, anchor="ne")  # Align to the top-right corner of the window

        # Adjust the size and position of the listbox
        self.low_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=25, height=10)  # Reduced height
        self.low_listbox.place(relx=1.0, rely=0.1, anchor="ne")  # Align below the label

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
        tk.Button(btn_frame, text="Mark as Open", command=self.mark_task_open).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Archive Task", command=self.archive_selected_task).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Show Archive", command=self.show_archive).grid(row=0, column=6, padx=5)
        tk.Button(btn_frame, text="Settings", command=self.show_settings).grid(row=0, column=7, padx=5)

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
        self.venn_canvas.create_text(center_x + 150, center_y - medium_radius - 20, text="FITNESS: Make Time",
                                     fill="green",
                                     font=("Helvetica", 14, "bold"))

        self.venn_canvas.create_oval(center_x - medium_radius, center_y - medium_radius + 150,
                                     center_x + medium_radius, center_y + medium_radius + 150,
                                     fill=urgency_color, outline="", tags="urgency_area")
        self.venn_canvas.create_text(center_x, center_y + medium_radius + 30, text="URGENT: Delegate Next", fill="red",
                                     font=("Helvetica", 14, "bold"))

        # Text labels for Do Now section, adjusted to match new circle positions
        self.venn_canvas.create_text(center_x, center_y + 100, text="Do Now", fill="black",
                                     font=("Helvetica", 16, "bold"))

    def update_task_venn_diagram(self):
        """
        Updates the Venn diagram with current tasks and initializes drag-and-drop bindings.
        Ensures tasks are correctly displayed based on their priorities without overlapping.
        """
        self.venn_canvas.delete("task_text")
        self.low_listbox.delete(0, tk.END)
        self.task_elements.clear()  # Reset task mapping

        # Initialize DragDropHandler if not already initialized
        # Initialize DragDropHandler
        self.drag_drop_handler = DragDropHandler(
            self.venn_canvas,
            self.task_elements,
            self,
            db_path=self.db_path
        )

        # Define the center of the Venn Diagram
        venn_center_x, venn_center_y = 512, 512
        medium_radius = 375
        hhh_radius = 75  # Radius for "Do Now" circular placement
        hhh_angle_step = 30  # Angle step for placing tasks in "HHH"

        # Centers for priority areas
        importance_center = (venn_center_x - medium_radius, venn_center_y)
        urgency_center = (venn_center_x, venn_center_y + medium_radius)
        fitness_center = (venn_center_x + medium_radius, venn_center_y)

        # Offset for spreading tasks within the same priority region
        offset_step = 15
        placement_offsets = {
            "HHH": 0,  # Angle counter for circular placement
            "HH": 0,
            "HF": 0,
            "UF": 0,
            "I": 0,
            "U": 0,
            "F": 0
        }

        for task in self.tasks:
            # Determine task placement based on priorities
            if task.importance == Priority.HIGH and task.urgency == Priority.HIGH and task.fitness == Priority.HIGH:
                # "Do Now" central placement in a circular layout
                angle_rad = math.radians(hhh_angle_step * placement_offsets["HHH"])
                x = venn_center_x + hhh_radius * math.cos(angle_rad)
                y = venn_center_y + hhh_radius * math.sin(angle_rad) + 75
                placement_offsets["HHH"] += 1.5
            elif task.importance == Priority.HIGH and task.urgency == Priority.HIGH:
                # Overlap region between Importance and Urgency
                x = (importance_center[0] + urgency_center[0]) / 2
                y = (importance_center[1] + urgency_center[1]) / 2 + placement_offsets["HH"]
                placement_offsets["HH"] += offset_step
            elif task.importance == Priority.HIGH and task.fitness == Priority.HIGH:
                # Overlap region between Importance and Fitness
                x = (importance_center[0] + fitness_center[0]) / 2
                y = (importance_center[1] + fitness_center[1]) / 2 + placement_offsets["HF"]
                placement_offsets["HF"] += offset_step
            elif task.urgency == Priority.HIGH and task.fitness == Priority.HIGH:
                # Overlap region between Urgency and Fitness
                x = (urgency_center[0] + fitness_center[0]) / 2
                y = (urgency_center[1] + fitness_center[1]) / 2 + placement_offsets["UF"]
                placement_offsets["UF"] += offset_step
            elif task.importance == Priority.HIGH:
                # Importance circle
                x = importance_center[0]
                y = importance_center[1] + placement_offsets["I"]
                placement_offsets["I"] += offset_step
            elif task.urgency == Priority.HIGH:
                # Urgency circle
                x = urgency_center[0]
                y = urgency_center[1] + placement_offsets["U"]
                placement_offsets["U"] += offset_step
            elif task.fitness == Priority.HIGH:
                # Fitness circle
                x = fitness_center[0]
                y = fitness_center[1] + placement_offsets["F"]
                placement_offsets["F"] += offset_step
            else:
                # LOW priority tasks go into the listbox
                if task.title not in self.low_listbox.get(0, tk.END):
                    self.low_listbox.insert(tk.END, task.title)
                continue

            # Create a text element for the task and map it
            text_id = self.venn_canvas.create_text(x, y, text=task.title, tags="task_text")
            self.task_elements[task.id] = text_id  # Map the task ID to its text element

            # Bind drag-and-drop events to the task
            self.venn_canvas.tag_bind(
                text_id, "<Button-1>", lambda event, tid=task.id: self.drag_or_select_task(event, tid)
            )
            self.venn_canvas.tag_bind(
                text_id, "<B1-Motion>", lambda event, tid=task.id: self.drag_drop_handler.drag_task(event, tid)
            )
            self.venn_canvas.tag_bind(
                text_id, "<ButtonRelease-1>", lambda event, tid=task.id: self.drag_drop_handler.drop_task(event, tid)
            )


    def load_tasks(self, filters=None):
        """
        Loads tasks from the database based on the given filters.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        self.tasks.clear()

        # Base query
        query = '''
            SELECT id, title, description, due_date, importance, urgency, fitness, status 
            FROM tasks 
            WHERE user_id = ?
        '''
        params = [self.current_user_id]

        # Apply filters if any
        if filters:
            if 'importance' in filters:
                query += ' AND UPPER(importance) = ?'
                params.append(filters['importance'].upper())
            if 'urgency' in filters:
                query += ' AND UPPER(urgency) = ?'
                params.append(filters['urgency'].upper())
            if 'fitness' in filters:
                query += ' AND UPPER(fitness) = ?'
                params.append(filters['fitness'].upper())
            if 'search' in filters:
                query += ' AND title LIKE ?'
                params.append(f"%{filters['search']}%")
            if 'status' in filters:
                query += ' AND UPPER(status) = ?'
                params.append(filters['status'].upper())
            if 'due_date' in filters:
                query += ' AND due_date <= ?'
                params.append(filters['due_date'].strftime("%Y-%m-%d"))

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            task_id, title, description, due_date_str, importance_str, urgency_str, fitness_str, status_str = row
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

            # Convert database values to Priority Enum
            importance = Priority[importance_str.upper()]
            urgency = Priority[urgency_str.upper()]
            fitness = Priority[fitness_str.upper()]

            # Default to OPEN if status is None
            status = Status[status_str.upper()] if status_str else Status.OPEN

            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                importance=importance,
                urgency=urgency,
                fitness=fitness,
                status=status,
                task_id=task_id
            )
            self.tasks.append(task)

        conn.close()
        self.update_task_venn_diagram()

    def select_task(self, event, task_id):
        """
        Marks the task as selected and highlights it for editing.
        """
        # Deselect the previously selected task, if any
        if self.selected_task is not None:
            self.venn_canvas.itemconfig(self.selected_task["text_id"], fill="black")

        # Find the task by task_id in self.tasks
        selected_task = next((task for task in self.tasks if task.id == task_id), None)
        if not selected_task:
            print(f"[ERROR] Task with ID {task_id} not found in self.tasks!")
            return

        self.selected_task = {"task": selected_task, "text_id": self.task_elements[task_id]}
        self.venn_canvas.itemconfig(self.selected_task["text_id"], fill="red")  # Highlight selected task in red


    def edit_task_from_canvas(self, task):
        """
        Opens the TaskEditor for the specified task when clicked on the Venn diagram.
        """
        TaskEditor(self, "Edit Task", task=task)

    '''
    def task_listbox_select(self, event):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            self.selected_task_index = selected_index[0]
            # Clear selection in the LOW listbox
            self.low_listbox.selection_clear(0, tk.END)
        else:
            self.selected_task_index = None
    '''

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
        """
        Handles the selection of a task in the LOW Priority Tasks listbox.
        """
        selected_index = self.low_listbox.curselection()  # Get selected item index
        if not selected_index:
            self.selected_task = None  # Clear selection if nothing is selected
            return

        selected_title = self.low_listbox.get(selected_index)
        selected_task = next((task for task in self.tasks if task.title == selected_title), None)

        if selected_task:
            self.selected_task = {"task": selected_task, "text_id": None}  # No text_id for listbox items
            self.selected_task_index = self.tasks.index(selected_task)
        else:
            self.selected_task = None
            self.selected_task_index = None

        # Ensure the Venn diagram is updated and visible
        self.update_task_venn_diagram()


    def add_task(self):
        """
        Opens the TaskEditor with default priorities for adding a new task.
        """
        try:
            # Fetch user-specific default priorities from the settings table
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT default_importance, default_urgency, default_fitness 
                FROM settings 
                WHERE user_id = ?
            ''', (self.current_user_id,))
            row = cursor.fetchone()
            conn.close()

            # Set priorities based on the user's settings or fallback to defaults
            if row:
                default_importance = Priority[row[0].upper()] if row[0] else Priority.LOW
                default_urgency = Priority[row[1].upper()] if row[1] else Priority.LOW
                default_fitness = Priority[row[2].upper()] if row[2] else Priority.LOW
            else:
                # Fallback to defaults if no row exists
                default_importance = Priority.LOW
                default_urgency = Priority.LOW
                default_fitness = Priority.LOW

            print(
                f"Default values: Importance={default_importance}, Urgency={default_urgency}, Fitness={default_fitness}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching default priorities: {e}")
            default_importance = Priority.LOW
            default_urgency = Priority.LOW
            default_fitness = Priority.LOW

        # Open the TaskEditor with user-specific default priorities
        TaskEditor(
            self,
            "Add New Task",
            default_importance=default_importance,
            default_urgency=default_urgency,
            default_fitness=default_fitness
        )

    def edit_task(self):
        """
        Opens the TaskEditor for editing the selected task.
        """
        if not self.selected_task:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return

        selected_task = self.selected_task["task"]
        TaskEditor(self, "Edit Task", task=selected_task)

    def delete_task(self):
        """
        Deletes the selected task from the list and updates the diagram and listbox accordingly.
        Displays a confirmation dialog before deleting the task.
        """
        task_to_delete = None

        # Check if a task is selected in the Venn diagram or LOW priority listbox
        if self.selected_task:
            task_to_delete = self.selected_task["task"]
        elif self.low_listbox.curselection():
            selected_index = self.low_listbox.curselection()[0]
            selected_task_title = self.low_listbox.get(selected_index)
            task_to_delete = next((task for task in self.tasks if task.title == selected_task_title), None)

        if not task_to_delete:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        # Ask for confirmation before deleting
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the task '{task_to_delete.title}'?")
        if not confirm:
            return  # Do nothing if the user selects "No"

        try:
            # Remove the task from the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?',
                           (task_to_delete.id, self.current_user_id))
            conn.commit()
            conn.close()

            # Remove the task from the UI
            self.tasks.remove(task_to_delete)
            if self.selected_task:
                if self.selected_task["text_id"]:
                    self.venn_canvas.delete(self.selected_task["text_id"])  # Remove from Venn diagram
                self.selected_task = None  # Clear selection
            elif self.low_listbox.curselection():
                self.low_listbox.delete(selected_index)  # Remove from "LOW" listbox

            messagebox.showinfo("Task Deleted", f"Task '{task_to_delete.title}' has been deleted successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error deleting task: {e}")

        # Refresh the task display
        self.update_task_listbox()

    def mark_task_completed(self):
        task_to_mark = None

        if self.selected_task:
            task_to_mark = self.selected_task["task"]
        elif self.low_listbox.curselection():
            selected_index = self.low_listbox.curselection()[0]
            selected_task_title = self.low_listbox.get(selected_index)
            task_to_mark = next((task for task in self.tasks if task.title == selected_task_title), None)

        if not task_to_mark:
            messagebox.showwarning("No Selection", "Please select a task to mark as completed.")
            return

        task_to_mark.status = Status.COMPLETED

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks
                SET status = ?
                WHERE id = ? AND user_id = ?
            ''', (Status.COMPLETED.value, task_to_mark.id, self.current_user_id))
            conn.commit()
            conn.close()

            # Debug: Check if the user ID and auto_archive are correct
            settings = self.settings_manager.get_settings(self.current_user_id)
            print(f"[DEBUG] User ID: {self.current_user_id}, Settings: {settings}")

            if settings.get("auto_archive", False):
                print("[DEBUG] Auto-archiving is enabled.")
                self.archive_selected_task(task_to_archive=task_to_mark)
            else:
                print("[DEBUG] Auto-archiving is disabled.")
                messagebox.showinfo("Task Completed", f"Task '{task_to_mark.title}' has been marked as completed.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error marking task as completed: {e}")
            return

        self.update_task_listbox()

    def archive_selected_task(self, task_to_archive=None):
        """
        Archives the given task (or the selected task if none is provided) if it is completed
        and updates the diagram and listbox accordingly.
        """
        if not task_to_archive:
            # Check if a task is selected in the Venn diagram
            if self.selected_task:
                task_to_archive = self.selected_task["task"]
            elif self.low_listbox.curselection():
                selected_index = self.low_listbox.curselection()[0]
                selected_task_title = self.low_listbox.get(selected_index)
                task_to_archive = next((task for task in self.tasks if task.title == selected_task_title), None)

        if not task_to_archive:
            messagebox.showwarning("No Selection", "Please select a task to archive.")
            return

        # Ensure the task is completed before archiving
        if task_to_archive.status != Status.COMPLETED:
            messagebox.showerror("Error", f"Task '{task_to_archive.title}' is not completed and cannot be archived.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert the task into the archived_tasks table with the user_id
            cursor.execute('''
                INSERT INTO archived_tasks (title, description, due_date, importance, urgency, fitness, status, completed_date, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_to_archive.title,
                task_to_archive.description,
                task_to_archive.due_date.strftime("%Y-%m-%d") if task_to_archive.due_date else None,
                task_to_archive.importance.value,
                task_to_archive.urgency.value,
                task_to_archive.fitness.value,
                task_to_archive.status.value,
                datetime.now().strftime("%Y-%m-%d"),
                self.current_user_id
            ))

            # Delete the task from the main tasks table
            cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?',
                           (task_to_archive.id, self.current_user_id))

            conn.commit()
            conn.close()

            # Remove the task from the task list and UI
            self.tasks.remove(task_to_archive)
            if self.selected_task:
                self.venn_canvas.delete(self.selected_task["text_id"])  # Remove from Venn diagram
                self.selected_task = None  # Clear selection
            elif self.low_listbox.curselection():
                self.low_listbox.delete(selected_index)  # Remove from "LOW" listbox

            messagebox.showinfo("Success", f"Task '{task_to_archive.title}' has been archived.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error archiving task: {e}")

        # Refresh the task display
        self.update_task_listbox()

    def show_archive(self):
        """
        Opens the ArchiveViewer with filtering functionality.
        """
        archive_viewer = ArchiveViewer(self)
        archive_viewer.load_archived_tasks()

    def show_settings(self):
        SettingsWindow(self)

    def schedule_notifications(self):
        notifications = self.notification_manager.schedule_notifications(self.tasks)
        for notification in notifications:
            messagebox.showinfo("Notification", f"Task '{notification['task'].title}' is due on {notification['due_date']}.")

    def mark_task_open(self):
        """
        Delegates marking a task as open to the TaskEditor.
        """
        # Check if a task is selected
        if self.selected_task:
            task_to_update = self.selected_task["task"]
        elif self.low_listbox.curselection():
            selected_index = self.low_listbox.curselection()[0]
            selected_task_title = self.low_listbox.get(selected_index)
            task_to_update = next((task for task in self.tasks if task.title == selected_task_title), None)
        else:
            messagebox.showwarning("No Selection", "Please select a completed task to mark as open.")
            return

        # Call TaskEditor's method
        if task_to_update:
            if task_to_update.status != Status.COMPLETED:
                messagebox.showerror("Error", "Only completed tasks can be marked as open.")
                return

            # Delegate task status change to TaskEditor
            TaskEditor.mark_task_open(task_to_update, self)

    def drag_or_select_task(self, event, task_id):
        """
        Handles whether a task is clicked (select) or dragged.
        """
        # Start the drag process
        self.drag_drop_handler.start_drag(event, task_id)

        # Delayed check for "drag vs. click"
        self.root.after(200, lambda: self._handle_click_or_drag(event, task_id))

    def _handle_click_or_drag(self, event, task_id):
        """
        Finalizes whether it was a click or drag.
        """
        if not self.drag_drop_handler.is_dragging:
            # No dragging detected -> Select the task
            self.select_task(event, task_id)
        else:
            print("Task dragged, skipping selection.")

