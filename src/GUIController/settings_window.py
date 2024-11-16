import tkinter as tk
from tkinter import messagebox

class SettingsWindow(tk.Toplevel):
    """
    A window for managing user settings, including notification preferences and auto-archive settings.
    """
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.settings_manager = controller.settings_manager
        self.title("Settings")
        self.geometry("300x300")
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        """
        Creates widgets for settings options.
        """
        # Notification interval setting
        tk.Label(self, text="Notification Interval (days):").pack(pady=5)
        self.notification_interval_var = tk.IntVar()
        self.notification_interval_entry = tk.Entry(self, textvariable=self.notification_interval_var)
        self.notification_interval_entry.pack(pady=5)

        # Enable/disable notifications setting
        self.notifications_enabled_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Enable Notifications", variable=self.notifications_enabled_var).pack(pady=5)

        # Auto-archive setting
        self.auto_archive_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Auto-archive completed tasks", variable=self.auto_archive_var).pack(pady=5)

        # Save settings button
        tk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=10)

    def load_settings(self):
        """
        Loads the current settings from the settings manager.
        """
        settings = self.settings_manager.get_settings()
        self.notification_interval_var.set(settings.get("notification_interval", 1))
        self.notifications_enabled_var.set(settings.get("notifications_enabled", True))
        self.auto_archive_var.set(settings.get("auto_archive", False))

    def save_settings(self):
        """
        Saves the current settings to the settings manager.
        """
        notification_interval = self.notification_interval_var.get()
        notifications_enabled = self.notifications_enabled_var.get()
        auto_archive = self.auto_archive_var.get()

        # Save settings via settings manager
        self.settings_manager.save_settings(
            notification_interval=notification_interval,
            auto_archive=auto_archive,
            auto_delete=False,  # Default value for now
            notifications_enabled=notifications_enabled,
            default_priorities={"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}  # Default priorities
        )

        messagebox.showinfo("Settings Saved", "Your settings have been saved.")
        self.destroy()
