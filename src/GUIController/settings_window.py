import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class SettingsWindow(tk.Toplevel):
    """
    A window for managing user settings, including notification preferences, auto-archive, auto-delete,
    and default priorities.
    """
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.db_path = controller.db_path  # Path to the database
        self.user_id = controller.current_user_id  # Get the currently logged-in user
        self.title("Settings")
        self.geometry("300x500")
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

        # Auto-delete setting
        self.auto_delete_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Auto-delete archived tasks", variable=self.auto_delete_var).pack(pady=5)

        # Auto-delete interval setting
        tk.Label(self, text="Auto-delete interval (days):").pack(pady=5)
        self.auto_delete_interval_var = tk.IntVar()
        self.auto_delete_interval_entry = tk.Entry(self, textvariable=self.auto_delete_interval_var)
        self.auto_delete_interval_entry.pack(pady=5)

        # Default priorities settings
        tk.Label(self, text="Default Importance Priority:").pack(pady=5)
        self.default_importance_var = tk.StringVar()
        self.importance_combo = ttk.Combobox(self, textvariable=self.default_importance_var, state="readonly")
        self.importance_combo['values'] = ['None', 'Low', 'High']
        self.importance_combo.pack(pady=5)

        tk.Label(self, text="Default Urgency Priority:").pack(pady=5)
        self.default_urgency_var = tk.StringVar()
        self.urgency_combo = ttk.Combobox(self, textvariable=self.default_urgency_var, state="readonly")
        self.urgency_combo['values'] = ['None', 'Low', 'High']
        self.urgency_combo.pack(pady=5)

        tk.Label(self, text="Default Fitness Priority:").pack(pady=5)
        self.default_fitness_var = tk.StringVar()
        self.fitness_combo = ttk.Combobox(self, textvariable=self.default_fitness_var, state="readonly")
        self.fitness_combo['values'] = ['None', 'Low', 'High']
        self.fitness_combo.pack(pady=5)

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
            cursor.execute('''
                SELECT notification_interval, auto_archive, auto_delete, auto_delete_interval, notifications_enabled, 
                       default_importance, default_urgency, default_fitness
                FROM settings WHERE user_id = ?
            ''', (self.user_id,))
            row = cursor.fetchone()

            # Set default values if no settings exist for the user
            if row:
                self.notification_interval_var.set(row[0] if row[0] is not None else 1)
                self.auto_archive_var.set(bool(row[1]) if row[1] is not None else False)
                self.auto_delete_var.set(bool(row[2]) if row[2] is not None else False)
                self.auto_delete_interval_var.set(row[3] if row[3] is not None else 30)
                self.notifications_enabled_var.set(bool(row[4]) if row[4] is not None else True)
                self.default_importance_var.set(row[5] if row[5] else 'None')
                self.default_urgency_var.set(row[6] if row[6] else 'None')
                self.default_fitness_var.set(row[7] if row[7] else 'None')
            else:
                # Insert default settings for the user if no record exists
                cursor.execute('''
                    INSERT INTO settings (user_id, notification_interval, auto_archive, auto_delete, 
                                          auto_delete_interval, notifications_enabled, 
                                          default_importance, default_urgency, default_fitness)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.user_id, 1, 0, 0, 30, 1, 'None', 'None', 'None'))
                conn.commit()
                self.notification_interval_var.set(1)
                self.auto_archive_var.set(False)
                self.auto_delete_var.set(False)
                self.auto_delete_interval_var.set(30)
                self.notifications_enabled_var.set(True)
                self.default_importance_var.set('None')
                self.default_urgency_var.set('None')
                self.default_fitness_var.set('None')

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
        auto_delete = self.auto_delete_var.get()
        auto_delete_interval = self.auto_delete_interval_var.get()
        default_importance = self.default_importance_var.get()
        default_urgency = self.default_urgency_var.get()
        default_fitness = self.default_fitness_var.get()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update settings for the current user
            cursor.execute('''
                UPDATE settings
                SET notification_interval = ?, auto_archive = ?, auto_delete = ?, auto_delete_interval = ?, 
                    notifications_enabled = ?, default_importance = ?, default_urgency = ?, default_fitness = ?
                WHERE user_id = ?
            ''', (notification_interval, int(auto_archive), int(auto_delete), auto_delete_interval,
                  int(notifications_enabled), default_importance, default_urgency, default_fitness, self.user_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Settings Saved", "Your settings have been saved.")
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving settings: {e}")
