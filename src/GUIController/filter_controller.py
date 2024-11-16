import tkinter as tk
from datetime import datetime


class FilterController:
    """
    Handles the search and filter functionality for tasks and archived tasks.
    """

    def __init__(self, gui_controller, is_archive=False):
        self.gui_controller = gui_controller
        self.is_archive = is_archive  # Determine if filtering applies to the archive or active tasks
        self.filters = {}

        # Create filter widgets
        self.create_filter_widgets()

    def create_filter_widgets(self):
        """
        Creates the widgets for the search and filter functionality.
        """
        filter_frame = tk.Frame(self.gui_controller.root)
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

    def apply_filters(self):
        """
        Applies the search and filter criteria and reloads the task list.
        """
        filters = {}

        # Search filter
        search_text = self.search_entry.get().strip()
        if search_text:
            filters['search'] = search_text

        # Priority filters
        importance = self.importance_var.get()
        if importance != "All":
            filters['importance'] = importance

        urgency = self.urgency_var.get()
        if urgency != "All":
            filters['urgency'] = urgency

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

        # Save and apply filters
        self.filters = filters
        self.gui_controller.load_tasks(filters)

    def reset_filters(self):
        """
        Resets all filter options and reloads the full task list or archive.
        """
        self.search_entry.delete(0, tk.END)
        for priority in ["importance", "urgency", "fitness"]:
            getattr(self, f"{priority}_var").set("All")
        self.filters = {}

        if self.is_archive:
            self.gui_controller.load_archived_tasks()
        else:
            self.gui_controller.load_tasks()
