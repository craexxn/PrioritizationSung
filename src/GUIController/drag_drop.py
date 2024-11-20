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

    def __init__(self, canvas, task_elements, update_callback, db_path):
        """
        Initializes the DragDropHandler.

        :param canvas: The canvas where tasks are displayed.
        :param task_elements: A dictionary mapping task titles to their canvas text IDs.
        :param update_callback: A callback function to refresh the Venn diagram after a drop.
        :param db_path: The path to the SQLite database.
        """
        print(f"DragDropHandler initialized with canvas: {canvas}")
        self.canvas = canvas
        self.task_elements = task_elements
        self.update_callback = update_callback
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Database/database.db'))
        self.dragging_task_id = None
        self.start_x = None
        self.start_y = None
        self.is_dragging = False  # Flag to differentiate between click and drag
        self.drag_threshold = 5  # Minimum distance to start dragging

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
        print(f"Started dragging task ID: {task_id}")

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
        print(f"Dragging task ID: {task_id} to ({event.x}, {event.y})")

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
        print(f"Dropped task ID: {task_id} at ({x}, {y}) in area: {new_priority_area}")

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
            print(f"Task ID {task_id} updated in database with new priorities {new_priority_area}.")

            # Refresh the Venn diagram immediately
            self.update_callback()
            print("Venn diagram updated after drop.")

        except sqlite3.Error as e:
            print(f"Error updating database for task ID {task_id}: {e}")


    def reset_drag_state(self):
        """
        Resets the dragging state.
        """
        self.dragging_task_id = None
        self.start_x = None
        self.start_y = None
        self.is_dragging = False


    def get_priority_from_position(self, x, y):
        """
        Determines the task priority based on the drop position.

        :param x: The x-coordinate of the drop position.
        :param y: The y-coordinate of the drop position.
        :return: A tuple representing the new priority (Priority.IMPORTANCE, Priority.URGENCY, Priority.FITNESS).
        """
        # Center of the Venn diagram
        center_x, center_y = 512, 512
        medium_radius = 275

        # Distance calculation for each circle
        distance_to_importance = math.sqrt((x - (center_x - medium_radius - 150)) ** 2 + (y - center_y) ** 2)
        distance_to_urgency = math.sqrt((x - center_x) ** 2 + (y - (center_y + medium_radius)) ** 2)
        distance_to_fitness = math.sqrt((x - (center_x + medium_radius + 150)) ** 2 + (y - center_y) ** 2)

        # Threshold for determining which circle the task is dropped into
        threshold = medium_radius

        # Determine priority based on the closest circle
        importance = Priority.LOW
        urgency = Priority.LOW
        fitness = Priority.LOW

        if distance_to_importance < threshold:
            importance = Priority.HIGH
        if distance_to_urgency < threshold:
            urgency = Priority.HIGH
        if distance_to_fitness < threshold:
            fitness = Priority.HIGH

        return importance, urgency, fitness

def get_priority_areas(self):
    """
    Returns predefined priority areas based on the Venn diagram layout.
    Each area is defined as a center and a radius (for circles).
    """
    # Centers of the Venn Diagram
    venn_center_x, venn_center_y = 512, 512
    medium_radius = 375
    hhh_radius = 75  # Radius for "Do Now" circular placement

    # Define circle centers
    importance_center = (venn_center_x - medium_radius, venn_center_y)
    urgency_center = (venn_center_x, venn_center_y + medium_radius)
    fitness_center = (venn_center_x + medium_radius, venn_center_y)

    # Define regions
    areas = {
        "HHH": {"center": (venn_center_x, venn_center_y), "radius": hhh_radius},
        "HH": {"center": ((importance_center[0] + urgency_center[0]) / 2,
                          (importance_center[1] + urgency_center[1]) / 2),
               "radius": medium_radius / 2},
        "HF": {"center": ((importance_center[0] + fitness_center[0]) / 2,
                          (importance_center[1] + fitness_center[1]) / 2),
               "radius": medium_radius / 2},
        "UF": {"center": ((urgency_center[0] + fitness_center[0]) / 2,
                          (urgency_center[1] + fitness_center[1]) / 2),
               "radius": medium_radius / 2},
        "Importance": {"center": importance_center, "radius": medium_radius},
        "Urgency": {"center": urgency_center, "radius": medium_radius},
        "Fitness": {"center": fitness_center, "radius": medium_radius},
        "LowPriority": {"center": (1000, 100), "radius": 0},  # Example for LOW
    }
    return areas


def is_point_in_circle(self, x, y, center, radius):
    """
    Checks if a point is within a circle's radius.

    :param x: x-coordinate of the point.
    :param y: y-coordinate of the point.
    :param center: Center of the circle (tuple).
    :param radius: Radius of the circle.
    :return: True if point is within the circle, False otherwise.
    """
    return (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius ** 2

