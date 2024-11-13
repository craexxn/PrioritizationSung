import os
import sys
import tkinter as tk
from tkinter import messagebox

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../User/UserRepository')))

from user_repository import UserRepository


class LoginWindow(tk.Toplevel):
    """
    A window for user login at the beginning of the session.
    """

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.title("Login")
        self.geometry("300x200")
        self.user_repo = UserRepository(controller.db_path)

        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Register", command=self.register).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.user_repo.get_user_by_username(username)

        if user and user.check_password(password):
            self.controller.current_user = username
            self.controller.load_tasks()  # Load tasks for this user
            self.destroy()  # Close the login window
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_repo.get_user_by_username(username):
            messagebox.showwarning("Warning", "Username already exists.")
        else:
            user = User(username, password)
            self.user_repo.save_user(user)
            messagebox.showinfo("Success", "User registered successfully.")