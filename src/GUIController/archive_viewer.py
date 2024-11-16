import os
import sys
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Import paths for other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Task')))

from task import Task, Priority, Status


class ArchiveViewer(tk.Toplevel):
    """
    A window for viewing archived tasks with search and filter functionality.
    """

    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        self.title("Archived Tasks")
        self.geometry("1024x512")

        self.filters = {}
        self.create_widgets()
        self.load_archived_tasks()

    def create_widgets(self):
        """
        Creates widgets for displaying archived tasks and filtering options.
        """
        # Filter frame
        filter_frame = tk.Frame(self)
        filter_frame.pack(side="top", fill="x", pady=5)

        # Search field
        tk.Label(filter_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(filter_frame, width=20)
        self.search_entry.pack(side="left", padx=5)

        # Filter: Importance
        tk.Label(filter_frame, text="Importance:").pack(side="left", padx=5)
        self.importance_var = tk.StringVar(value="All")
        importance_options = ["All", "High", "Low"]
        tk.OptionMenu(filter_frame, self.importance_var, *importance_options).pack(side="left", padx=5)

        # Filter: Urgency
        tk.Label(filter_frame, text="Urgency:").pack(side="left", padx=5)
        self.urgency_var = tk.StringVar(value="All")
        urgency_options = ["All", "High", "Low"]
        tk.OptionMenu(filter_frame, self.urgency_var, *urgency_options).pack(side="left", padx=5)

        # Filter: Fitness
        tk.Label(filter_frame, text="Fitness:").pack(side="left", padx=5)
        self.fitness_var = tk.StringVar(value="All")
        fitness_options = ["All", "High", "Low"]
        tk.OptionMenu(filter_frame, self.fitness_var, *fitness_options).pack(side="left", padx=5)

        # Filter: Due Date
        tk.Label(filter_frame, text="Due Date (before):").pack(side="left", padx=5)
        self.due_date_entry = tk.Entry(filter_frame, width=15)
        self.due_date_entry.pack(side="left", padx=5)

        # Apply and Reset Buttons
        tk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Reset Filters", command=self.reset_filters).pack(side="left", padx=5)

        # Listbox for archived tasks
        self.archived_listbox = tk.Listbox(self, width=80, height=15)
        self.archived_listbox.pack(pady=10)

        # Reactivate and Close buttons
        tk.Button(self, text="Reactivate Task", command=self.reactivate_task).pack(pady=5)
        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)

    def load_archived_tasks(self):
        """
        Loads archived tasks from the database based on the current filters.
        """
        self.archived_listbox.delete(0, tk.END)
        conn = sqlite3.connect(self.controller.db_path)
        cursor = conn.cursor()

        # Base query
        query = '''
            SELECT title, description, due_date, importance, urgency, fitness, status 
            FROM archived_tasks 
            WHERE user_id = ?
        '''
        params = [self.controller.current_user_id]

        # Apply filters
        if self.filters:
            if 'search' in self.filters:
                query += ' AND title LIKE ?'
                params.append(f"%{self.filters['search']}%")
            if 'importance' in self.filters:
                query += ' AND UPPER(importance) = ?'
                params.append(self.filters['importance'].upper())
            if 'urgency' in self.filters:
                query += ' AND UPPER(urgency) = ?'
                params.append(self.filters['urgency'].upper())
            if 'fitness' in self.filters:
                query += ' AND UPPER(fitness) = ?'
                params.append(self.filters['fitness'].upper())
            if 'due_date' in self.filters:
                query += ' AND due_date <= ?'
                params.append(self.filters['due_date'].strftime("%Y-%m-%d"))

        print(f"Executing query: {query} with params: {params}")  # Debug print
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.archived_tasks = []  # Store the loaded tasks
        for row in rows:
            title, description, due_date_str, importance_str, urgency_str, fitness_str, status_str = row
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            importance = Priority[importance_str.upper()]
            urgency = Priority[urgency_str.upper()]
            fitness = Priority[fitness_str.upper()]
            status = Status[status_str.upper()]

            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                importance=importance,
                urgency=urgency,
                fitness=fitness,
                status=status
            )
            self.archived_tasks.append(task)
            self.archived_listbox.insert(tk.END, f"{title} - {due_date_str} - {importance_str}, {urgency_str}, {fitness_str}")

    def apply_filters(self):
        """
        Applies the search and filter criteria to the archived tasks.
        """
        filters = {}

        # Search filter
        search_text = self.search_entry.get().strip()
        if search_text:
            filters['search'] = search_text

        # Importance filter
        importance = self.importance_var.get()
        if importance != "All":
            filters['importance'] = importance

        # Urgency filter
        urgency = self.urgency_var.get()
        if urgency != "All":
            filters['urgency'] = urgency

        # Fitness filter
        fitness = self.fitness_var.get()
        if fitness != "All":
            filters['fitness'] = fitness

        # Due date filter
        due_date = self.due_date_entry.get().strip()
        if due_date:
            try:
                filters['due_date'] = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date in the format YYYY-MM-DD.")
                return

        self.filters = filters
        self.load_archived_tasks()

    def reset_filters(self):
        """
        Resets all filter options and reloads the full archived task list.
        """
        self.search_entry.delete(0, tk.END)
        self.importance_var.set("All")
        self.urgency_var.set("All")
        self.fitness_var.set("All")
        self.due_date_entry.delete(0, tk.END)
        self.filters = {}
        self.load_archived_tasks()

    def reactivate_task(self):
        """
        Reactivates the selected archived task and opens it in the TaskEditor for further editing.
        """
        selected_index = self.archived_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a task to reactivate.")
            return

        selected_task = self.archived_tasks[selected_index[0]]
        try:
            conn = sqlite3.connect(self.controller.db_path)
            cursor = conn.cursor()

            # Insert the task back into the tasks table
            cursor.execute('''
                INSERT INTO tasks (title, description, due_date, importance, urgency, fitness, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                selected_task.title,
                selected_task.description,
                selected_task.due_date.strftime("%Y-%m-%d") if selected_task.due_date else None,
                selected_task.importance.value,
                selected_task.urgency.value,
                selected_task.fitness.value,
                Status.OPEN.value,  # Reset status to open
                self.controller.current_user_id
            ))

            # Remove the task from the archived_tasks table
            cursor.execute('DELETE FROM archived_tasks WHERE title = ? AND user_id = ?',
                           (selected_task.title, self.controller.current_user_id))

            conn.commit()
            conn.close()

            self.archived_tasks.pop(selected_index[0])
            self.archived_listbox.delete(selected_index)
            messagebox.showinfo("Success", f"Task '{selected_task.title}' has been reactivated.")
            self.controller.load_tasks()  # Refresh the main task list
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error reactivating task: {e}")
