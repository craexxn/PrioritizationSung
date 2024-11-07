import sqlite3
import json


class SettingsManager:
    """
    SettingsManager manages the user-specific settings for the application.
    """

    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self._initialize_settings_table()

    def _initialize_settings_table(self):
        """
        Ensures that the settings table exists in the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                notification_interval INTEGER DEFAULT 1,
                auto_archive BOOLEAN DEFAULT 1,
                auto_delete BOOLEAN DEFAULT 0,
                notifications_enabled BOOLEAN DEFAULT 1,
                default_priorities TEXT DEFAULT '{"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}'
            )
        ''')
        conn.commit()
        conn.close()

    def save_settings(self, notification_interval: int, auto_archive: bool, auto_delete: bool,
                      notifications_enabled: bool, default_priorities: dict):
        """
        Saves or updates the user settings in the database.

        :param notification_interval: Interval (in days) for notifications.
        :param auto_archive: Boolean indicating if tasks should be auto-archived.
        :param auto_delete: Boolean indicating if archived tasks should be auto-deleted.
        :param notifications_enabled: Boolean indicating if notifications are enabled.
        :param default_priorities: Dictionary with default priority values for new tasks.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert default priorities to JSON for storage
        default_priorities_json = json.dumps(default_priorities)

        # Check if settings already exist
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        if cursor.fetchone():
            # Update settings
            cursor.execute('''
                UPDATE settings
                SET notification_interval = ?, auto_archive = ?, auto_delete = ?, notifications_enabled = ?, default_priorities = ?
                WHERE id = 1
            ''', (notification_interval, int(auto_archive), int(auto_delete), int(notifications_enabled),
                  default_priorities_json))
        else:
            # Insert new settings
            cursor.execute('''
                INSERT INTO settings (id, notification_interval, auto_archive, auto_delete, notifications_enabled, default_priorities)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (notification_interval, int(auto_archive), int(auto_delete), int(notifications_enabled),
                  default_priorities_json))

        conn.commit()
        conn.close()

    def get_settings(self):
        """
        Retrieves the current user settings from the database.

        :return: A dictionary with the current settings.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT notification_interval, auto_archive, auto_delete, notifications_enabled, default_priorities FROM settings WHERE id = 1')
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "notification_interval": row[0],
                "auto_archive": bool(row[1]),
                "auto_delete": bool(row[2]),
                "notifications_enabled": bool(row[3]),
                "default_priorities": json.loads(row[4])  # Convert JSON back to dict
            }
        else:
            # Return default settings if no settings exist
            return {
                "notification_interval": 1,
                "auto_archive": True,
                "auto_delete": False,
                "notifications_enabled": True,
                "default_priorities": {"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}
            }

    def update_default_priorities(self, priorities: dict):
        """
        Updates the default priority settings.

        :param priorities: Dictionary with default priority values for new tasks.
        """
        current_settings = self.get_settings()
        self.save_settings(
            current_settings["notification_interval"],
            current_settings["auto_archive"],
            current_settings["auto_delete"],
            current_settings["notifications_enabled"],
            priorities
        )

    def update_notifications_enabled(self, enabled: bool):
        """
        Enables or disables notifications.

        :param enabled: Boolean to enable or disable notifications.
        """
        current_settings = self.get_settings()
        self.save_settings(
            current_settings["notification_interval"],
            current_settings["auto_archive"],
            current_settings["auto_delete"],
            enabled,
            current_settings["default_priorities"]
        )

