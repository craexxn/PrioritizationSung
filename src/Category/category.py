class Category:
    """
    Represents a category within the Sung Diagram, which organizes tasks based on importance, urgency, and fitness.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initializes a new Category instance with a name and an optional description.

        :param name: Name of the category (e.g., "High Importance & High Urgency & High Fitness")
        :param description: Optional description of the category
        """
        self.name = name
        self.description = description
        self.tasks = []  # List to store tasks within this category

    def add_task(self, task):
        """
        Adds a task to the category.

        :param task: Task instance to add to the category
        """
        self.tasks.append(task)

    def remove_task(self, task):
        """
        Removes a task from the category if it exists.

        :param task: Task instance to remove from the category
        """
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self):
        """
        Returns the list of tasks within the category.

        :return: List of tasks in this category
        """
        return self.tasks
