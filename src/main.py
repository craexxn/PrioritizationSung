import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'GUIController')))

from gui_controller import GUIController

def main():
    root = tk.Tk()
    app = GUIController(root)  # GUIController will handle showing the login and main window
    root.mainloop()

if __name__ == "__main__":
    main()
