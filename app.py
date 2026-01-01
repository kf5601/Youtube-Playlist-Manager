import tkinter as tk
from tkinter import ttk

# main "home" screen that:
#   - shows the "Log in with Google" / OAuth button
#   - after login, shows remaining API quota
#   - shows a tab / section with all playlists
from ui.home import HomePage


APP_TITLE = "YouTube Playlist Manager"
APP_WIDTH = 1200
APP_HEIGHT = 700


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
    # Create main window
    root = tk.Tk()
    root.title(APP_TITLE)

    # Size & minimums
    root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
    root.minsize(900, 550)

    # Apply styles
    configure_style(root)

    # Create and mount the home page
    # HomePage is responsible for:
    #   - OAuth login
    #   - displaying remaining Google API quota
    #   - displaying playlists (and letting user choose one)
    home = HomePage(master=root)
    home.pack(fill="both", expand=True)

    # Start the Tk event loop
    root.mainloop()


if __name__ == "__main__":
    main()
