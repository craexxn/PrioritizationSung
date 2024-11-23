import os
import sys
import math
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))

from task import Priority


class DragDropHandler:
    """
    Handles drag-and-drop functionality for tasks within the Venn diagram.
    """

    def __init__(self, canvas, task_elements, gui_controller, db_path):
        """
        Initializes the DragDropHandler.

        :param canvas: The canvas where tasks are displayed.
        :param task_elements: A dictionary mapping task IDs to their canvas text IDs.
        :param gui_controller: Reference to the GUIController instance.
        :param db_path: Path to the SQLite database.
        """
        self.canvas = canvas
        self.task_elements = task_elements
        self.gui_controller = gui_controller
        self.db_path = db_path
        self.dragging_task_id = None
        self.start_x = None
        self.start_y = None
        self.is_dragging = False
        self.drag_threshold = 50  # Minimum distance to start dragging

    def start_drag(self, event, task_id):
        """
        Prepares for dragging of a task.

        :param event: The mouse event.
        :param task_id: The ID of the task being dragged.
        """
        self.is_dragging = False  # Reset dragging flag
        self.dragging_task_id = task_id
        self.start_x = event.x
        self.start_y = event.y

    def drag_task(self, event, task_id):
        """
        Handles the movement of a task during dragging.
        """
        if self.dragging_task_id != task_id:
            return  # Ignore if it's not the task currently being dragged

        # Calculate movement
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.canvas.move(self.task_elements[task_id], dx, dy)

        # Update starting position for the next motion event
        self.start_x = event.x
        self.start_y = event.y

    def drop_task(self, event, task_id):
        """
        Finalizes the task's position after dropping and updates its priority in the database.
        """
        if self.dragging_task_id != task_id:
            return  # Ignore if it's not the task currently being dragged

        # Stop dragging
        self.is_dragging = False
        self.dragging_task_id = None

        x, y = event.x, event.y
        new_priority_area = self.get_priority_from_position(x, y)

        # Update the task's priority in the database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update the task's priority in the database
            cursor.execute('''
                UPDATE tasks
                SET importance = ?, urgency = ?, fitness = ?
                WHERE id = ?
            ''', (new_priority_area[0].name, new_priority_area[1].name, new_priority_area[2].name, task_id))

            conn.commit()
            conn.close()

            # Update the task in memory
            task = next((task for task in self.gui_controller.tasks if task.id == task_id), None)
            if task:
                task.importance, task.urgency, task.fitness = new_priority_area

            # Refresh the Venn diagram
            self.gui_controller.update_task_venn_diagram()

        except sqlite3.Error as e:
            print(f"Error updating database for task ID {task_id}: {e}")

    def get_priority_from_position(self, x, y):
        """
        Determines the task priority based on the drop position.

        :param x: The x-coordinate of the drop position.
        :param y: The y-coordinate of the drop position.
        :return: A tuple representing the new priority (Priority.IMPORTANCE, Priority.URGENCY, Priority.FITNESS).
        """
        # Center of the Venn diagram
        venn_center_x, venn_center_y = 512, 512
        medium_radius = 375
        hhh_radius = 75

        # Define centers for each circle
        importance_center = (venn_center_x - medium_radius, venn_center_y)
        urgency_center = (venn_center_x, venn_center_y + medium_radius)
        fitness_center = (venn_center_x + medium_radius, venn_center_y)

        # Threshold for determining proximity to the center of a circle
        threshold = medium_radius

        # Distance calculations
        distance_to_importance = math.sqrt((x - importance_center[0]) ** 2 + (y - importance_center[1]) ** 2)
        distance_to_urgency = math.sqrt((x - urgency_center[0]) ** 2 + (y - urgency_center[1]) ** 2)
        distance_to_fitness = math.sqrt((x - fitness_center[0]) ** 2 + (y - fitness_center[1]) ** 2)

        # Initialize priorities
        importance = Priority.LOW
        urgency = Priority.LOW
        fitness = Priority.LOW

        # Determine proximity for "Do Now" (HHH)
        if (
                math.sqrt((x - venn_center_x) ** 2 + (y - venn_center_y - 75) ** 2) <= hhh_radius
        ):
            return Priority.HIGH, Priority.HIGH, Priority.HIGH

        # Determine other priorities
        if distance_to_importance < threshold:
            importance = Priority.HIGH
        if distance_to_urgency < threshold:
            urgency = Priority.HIGH
        if distance_to_fitness < threshold:
            fitness = Priority.HIGH

        # Return the determined priorities
        return importance, urgency, fitness




