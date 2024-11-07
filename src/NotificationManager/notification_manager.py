# notification_manager.py

from datetime import date, timedelta


class NotificationManager:
    """
    Manages notifications based on tasks and user settings.
    """

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def schedule_notifications(self, tasks):
        """
        Schedules notifications for tasks based on the notification interval in settings.

        :param tasks: List of Task objects to evaluate for notifications.
        :return: List of tasks that have scheduled notifications.
        """
        settings = self.settings_manager.get_settings()
        notifications = []

        if settings["notifications_enabled"]:
            interval = settings["notification_interval"]
            today = date.today()

            for task in tasks:
                # Notify if the task is due within the interval
                if task.due_date and (task.due_date - today).days <= interval:
                    notifications.append({"task": task, "due_date": task.due_date})

        return notifications
