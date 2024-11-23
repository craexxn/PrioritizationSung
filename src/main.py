import os
import sys
import tkinter as tk

# Validate and add the path for GUIController
gui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'GUIController'))
if not os.path.isdir(gui_path):
    raise ImportError(f"GUIController directory not found at {gui_path}")
sys.path.insert(0, gui_path)

from gui_controller import GUIController

def main():
    root = tk.Tk()
    try:
        # Attempt to initialize the GUIController
        app = GUIController(root)  # GUIController will handle showing the login and main window
        root.mainloop()
    except Exception as e:
        print(f"Failed to initialize GUIController: {e}")
        root.destroy()  # Ensure the Tkinter root is closed if initialization fails

if __name__ == "__main__":
    main()
