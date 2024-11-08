import tkinter as tk
from tkinter import messagebox

class SettingsWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.settings_manager = controller.settings_manager
        self.title("Settings")
        self.geometry("300x250")
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        tk.Label(self, text="Notification Interval (days):").pack(pady=5)
        self.notification_interval_var = tk.IntVar()
        self.notification_interval_entry = tk.Entry(self, textvariable=self.notification_interval_var)
        self.notification_interval_entry.pack(pady=5)

        self.notifications_enabled_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Enable Notifications", variable=self.notifications_enabled_var).pack(pady=5)

        tk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=10)

    def load_settings(self):
        settings = self.settings_manager.get_settings()
        self.notification_interval_var.set(settings.get("notification_interval", 1))
        self.notifications_enabled_var.set(settings.get("notifications_enabled", True))

    def save_settings(self):
        notification_interval = self.notification_interval_var.get()
        notifications_enabled = self.notifications_enabled_var.get()

        self.settings_manager.save_settings(
            notification_interval=notification_interval,
            auto_archive=True,
            auto_delete=False,
            notifications_enabled=notifications_enabled,
            default_priorities={"importance": "LOW", "urgency": "LOW", "fitness": "LOW"}
        )
        messagebox.showinfo("Settings Saved", "Your settings have been saved.")
        self.destroy()
