import os
import sys
import tkinter as tk
from tkinter import messagebox
import re

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../User')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../User/UserRepository')))

from user_repository import UserRepository
from user import User


class LoginWindow(tk.Toplevel):
    """
    A modal window for user login at the beginning of the session.
    """

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.title("Login")
        self.geometry("300x200")
        self.user_repo = UserRepository(controller.db_path)

        # Configure modal behavior
        self.transient(controller.root)  # Make this window modal relative to the main window
        self.grab_set()  # Lock the focus to this window until it is closed

        # Set the close event for the login window
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Widgets for login
        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Register", command=self.register).pack(pady=5)

    def validate_input(self, username, password):
        """
        Validates the username and password for length and allowed characters.

        :param username: The username input by the user.
        :param password: The password input by the user.
        :return: True if input is valid, False otherwise.
        """
        if not username or not password:
            messagebox.showwarning("Warning", "Username and password cannot be empty.")
            return False

        # Validate username: must be alphanumeric and 3-20 characters long
        if not re.match(r'^[a-zA-Z0-9]{3,20}$', username):
            messagebox.showwarning(
                "Warning",
                "Username must be 3-20 characters long and contain only alphanumeric characters."
            )
            return False

        # Validate password: must be at least 8 characters long
        if len(password) < 3:
            messagebox.showwarning(
                "Warning",
                "Password must be at least 3 characters long."
            )
            return False

        return True

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate input before proceeding
        if not self.validate_input(username, password):
            return

        user = self.user_repo.get_user_by_username(username)

        if user and user.check_password(password):
            self.controller.current_user = username
            self.controller.current_user_id = user.id  # Store the user_id in the controller
            self.controller.load_tasks()  # Load tasks for this user
            self.destroy()  # Close the login window
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate input before proceeding
        if not self.validate_input(username, password):
            return

        # Check if the username already exists
        if self.user_repo.get_user_by_username(username):
            messagebox.showwarning("Warning", "Username already exists.")
        else:
            user = User(username, password)
            self.user_repo.save_user(user)
            messagebox.showinfo("Success", "User registered successfully, please log in to continue.")

    def on_close(self):
        """
        Triggered when the login window is closed. Exits the application if no user is logged in.
        """
        self.controller.root.quit()  # Close the entire application
