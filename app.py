# app.py
# dependencies stuff
import tkinter as tk
from tkinter import ttk
from ui.home import HomePage

# UI constants set up
APP_TITLE = "YouTube Playlist Manager"
# SHRINK THIS IF YOUR SCREEN IS SMALLER THAN 1920x1080
APP_WIDTH = 1920
APP_HEIGHT = 1080

# setting up global styles page
def configure_style(root: tk.Tk) -> None:
    """Global ttk styles and theme."""
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except Exception:
        # if 'clam' is not available, just ignore
        pass

    style.configure("TLabel", padding=(4, 2))
    style.configure("TButton", padding=(8, 4))
    style.configure("TEntry", padding=(2, 2))
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))

# main app logic loop
def main() -> None:
    root = tk.Tk()
    root.title(APP_TITLE)

    root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    root.minsize(900, 650) # minimum size to keep UI usable

    configure_style(root) # apply global styles

    # HomePage manages:
    # - OAuth login
    # - showing estimated quota usage
    # - listing playlists
    # - opening playlist windows
    app = HomePage(master=root)
    app.pack(fill="both", expand=True)

    root.mainloop()

# main guard
if __name__ == "__main__":
    main()
