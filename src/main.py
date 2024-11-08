import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'GUIController')))

from gui_controller import GUIController  # Ensure you have the correct import path

def main():
    root = tk.Tk()
    app = GUIController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
