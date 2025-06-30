import sys
import tkinter as tk
from src.ssh_key_manager.gui.main_window import MainWindow

def main():
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"[ERROR] Application crashed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
