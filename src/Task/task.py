from enum import Enum
from datetime import date

class Priority(Enum):
    HIGH = "High"
    LOW = "Low"

class Status(Enum):
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"

class Task:
    """
    Represents a task that a user can create, edit, and categorize.
    """

    def __init__(self, title: str, due_date: date, importance: Priority, urgency: Priority, fitness: Priority,
                 description: str = ""):
        """
        Initializes a new Task instance with essential attributes.

        :param title: Title of the task
        :param due_date: Due date of the task
        :param importance: Priority level based on importance (HIGH/LOW)
        :param urgency: Priority level based on urgency (HIGH/LOW)
        :param fitness: User's fitness or capability assessment to complete the task (HIGH/LOW)
        :param description: Optional detailed description of the task
        """
        self.title = title
        self.due_date = due_date
        self.importance = importance
        self.urgency = urgency
        self.fitness = fitness
        self.description = description
        self.status = Status.OPEN
        self.completed_date = None

    def edit_task(self, title: str = None, due_date: date = None, importance: Priority = None,
                  urgency: Priority = None, fitness: Priority = None, description: str = None):
        """
        Edits the task with new values if provided.

        :param title: New title of the task
        :param due_date: New due date of the task
        :param importance: New priority level based on importance
        :param urgency: New priority level based on urgency
        :param fitness: New capability assessment for completing the task
        :param description: New detailed description of the task
        """
        if title:
            self.title = title
        if due_date:
            self.due_date = due_date
        if importance:
            self.importance = importance
        if urgency:
            self.urgency = urgency
        if fitness:
            self.fitness = fitness
        if description:
            self.description = description

    def mark_as_completed(self):
        """
        Marks the task as completed and sets the completed_date to today's date.
        """
        self.status = Status.COMPLETED
        self.completed_date = date.today()
