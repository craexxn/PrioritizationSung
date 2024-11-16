import sqlite3
import tkinter as tk
from tkinter import messagebox


class SettingsWindow(tk.Toplevel):
    """
    A window for managing user settings, including notification preferences and auto-archive settings.
    """
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.db_path = controller.db_path  # Path to the database
        self.user_id = controller.current_user_id  # Get the currently logged-in user
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
        Loads the current settings from the database for the logged-in user.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch settings for the current user
            cursor.execute('SELECT notification_interval, auto_archive, notifications_enabled FROM settings WHERE user_id = ?', (self.user_id,))
            row = cursor.fetchone()

            # Set default values if no settings exist for the user
            if row:
                self.notification_interval_var.set(row[0] if row[0] is not None else 1)
                self.auto_archive_var.set(bool(row[1]) if row[1] is not None else False)
                self.notifications_enabled_var.set(bool(row[2]) if row[2] is not None else True)
            else:
                # Insert default settings for the user if no record exists
                cursor.execute('''
                    INSERT INTO settings (user_id, notification_interval, auto_archive, notifications_enabled)
                    VALUES (?, ?, ?, ?)
                ''', (self.user_id, 1, 0, 1))
                conn.commit()
                self.notification_interval_var.set(1)
                self.auto_archive_var.set(False)
                self.notifications_enabled_var.set(True)

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading settings: {e}")

    def save_settings(self):
        """
        Saves the current settings to the database for the logged-in user.
        """
        notification_interval = self.notification_interval_var.get()
        notifications_enabled = self.notifications_enabled_var.get()
        auto_archive = self.auto_archive_var.get()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update settings for the current user
            cursor.execute('''
                UPDATE settings
                SET notification_interval = ?, auto_archive = ?, notifications_enabled = ?
                WHERE user_id = ?
            ''', (notification_interval, int(auto_archive), int(notifications_enabled), self.user_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Settings Saved", "Your settings have been saved.")
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving settings: {e}")
