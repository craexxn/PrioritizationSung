from enum import Enum
from datetime import date

class Priority(Enum):
    """
    Enum representing priority levels.
    """
    LOW = 'Low'
    HIGH = 'High'

class Status(Enum):
    """
    Enum representing task statuses.
    """
    OPEN = 'Open'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

class Task:
    """
    Represents a task with attributes such as title, due date, priority levels,
    description, status, and completion date.
    """

    def __init__(self, title, due_date, importance, urgency, fitness, description="",
                 status=Status.OPEN, completed_date=None, task_id=None):
        """
        Initializes a new Task instance.

        :param title: Title of the task.
        :param due_date: Due date of the task.
        :param importance: Importance level (Priority.HIGH or Priority.LOW).
        :param urgency: Urgency level (Priority.HIGH or Priority.LOW).
        :param fitness: Fitness level (Priority.HIGH or Priority.LOW).
        :param description: Optional description of the task.
        :param status: Current status of the task (default is Status.OPEN).
        :param completed_date: Date when the task was completed (default is None).
        :param task_id: Unique identifier for the task (default is None).
        """
        self.id = task_id
        self.title = title
        self.due_date = due_date
        self.importance = importance
        self.urgency = urgency
        self.fitness = fitness
        self.description = description
        self.status = status
        self.completed_date = completed_date

    def edit_task(self, title=None, due_date=None, importance=None,
                  urgency=None, fitness=None, description=None):
        """
        Edits the task's attributes with new values if provided.

        :param title: New title of the task.
        :param due_date: New due date of the task.
        :param importance: New importance level.
        :param urgency: New urgency level.
        :param fitness: New fitness level.
        :param description: New description of the task.
        """
        if title is not None:
            self.title = title
        if due_date is not None:
            self.due_date = due_date
        if importance is not None:
            self.importance = importance
        if urgency is not None:
            self.urgency = urgency
        if fitness is not None:
            self.fitness = fitness
        if description is not None:
            self.description = description

    def mark_as_completed(self):
        """
        Marks the task as completed and sets the completed_date to today's date.
        """
        self.status = Status.COMPLETED
        self.completed_date = date.today()
