import tkinter as tk

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

        # Filter: Importance, Urgency, Fitness
        for priority in ["Importance", "Urgency", "Fitness"]:
            tk.Label(filter_frame, text=f"{priority}:").pack(side="left", padx=5)
            var = tk.StringVar(value="All")
            setattr(self, f"{priority.lower()}_var", var)  # Store as attribute
            options = ["All", "High", "Low"]
            tk.OptionMenu(filter_frame, var, *options).pack(side="left", padx=5)

        # Apply and Reset Buttons
        tk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Reset Filters", command=self.reset_filters).pack(side="left", padx=5)

    def apply_filters(self):
        """
        Applies the search and filter criteria and reloads the task list or archive.
        """
        filters = {}

        # Search filter
        search_text = self.search_entry.get().strip()
        if search_text:
            filters['search'] = search_text

        # Priority filters
        for priority in ["importance", "urgency", "fitness"]:
            value = getattr(self, f"{priority}_var").get()
            if value != "All":
                filters[priority] = value.upper()

        # Apply filters to the appropriate view
        if self.is_archive:
            self.gui_controller.load_archived_tasks(filters)
        else:
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
