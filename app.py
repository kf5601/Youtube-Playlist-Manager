# app.py
import tkinter as tk
from tkinter import ttk

from ui.home import HomePage


APP_TITLE = "YouTube Playlist Manager"
APP_WIDTH = 1400
APP_HEIGHT = 800


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


def main() -> None:
    root = tk.Tk()
    root.title(APP_TITLE)

    root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    root.minsize(900, 550)

    configure_style(root)

    # HomePage manages:
    # - OAuth login
    # - showing estimated quota usage
    # - listing playlists
    # - opening playlist windows
    app = HomePage(master=root)
    app.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
