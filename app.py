import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Dict, Type, Optional


@dataclass
class Session:
    """
    Holds runtime session state for the app.

    Extend this with whatever you need later (e.g. selected playlist, etc.).
    """
    google_email: Optional[str] = None
    channel_title: Optional[str] = None
    channel_id: Optional[str] = None
    # add more fields as needed (selected_playlist_id, etc.)


class App(tk.Tk):
    """
    Main application window.

    Owns:
      - a Session object (self.session)
      - an abstract "YouTube client" reference (self.youtube_client)
      - a frame router with show_frame() / safe_show()
    """
    TITLE = "YouTube Playlist Manager"

    def _set_style(self):
        """ttk styles and theme."""
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            # if "clam" is not available, ignore
            pass

        # style tweaks
        style.configure("TLabel", padding=(4, 2))
        style.configure("TButton", padding=(6, 4))
        style.configure("TEntry", padding=(2, 2))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))

    def __init__(self):
        super().__init__()

        # Basic window setup
        self.title(self.TITLE)
        self.geometry("1280x650")
        self.minsize(1000, 560)
        self._set_style()

        # Session for the currently "logged-in" Google/YouTube user
        self.session = Session()

        # Placeholder for YouTube API client (whatever type you end up using)
        # This will be set from your Auth/Login frame after a successful OAuth flow.
        self.youtube_client: Optional[object] = None

        # Root container & router
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames: Dict[str, tk.Frame] = {}

        # Import UI frame classes here to avoid circular imports
        # (You will create these in separate files/modules.)
        #
        # Example structure:
        #   ui/auth.py            -> AuthFrame      (Google sign-in, logout)
        #   ui/playlists.py       -> PlaylistsFrame (list user playlists)
        #   ui/playlist_items.py  -> PlaylistItemsFrame (videos in selected playlist + CRUD UI)
        #
        # Adjust names/paths to whatever you actually use.
        from ui.auth import AuthFrame
        from ui.playlists import PlaylistsFrame
        from ui.playlist_items import PlaylistItemsFrame

        # Map route name -> Frame class
        routes: Dict[str, Type[tk.Frame]] = {
            "Auth": AuthFrame,
            "Playlists": PlaylistsFrame,
            "PlaylistItems": PlaylistItemsFrame,
        }

        for name, FrameCls in routes.items():
            frame = FrameCls(parent=container, app=self)  # pass app for shared state
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Start at Auth (login / connect Google account)
        self.show_frame("Auth")

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # === ROUTING HELPERS ===================================================

    def show_frame(self, name: str):
        """
        Raise a frame by name; calls `on_show()` on the frame if available.
        """
        frame = self.frames.get(name)
        if not frame:
            raise KeyError(f"Unknown frame '{name}'")

        # Allow pages to refresh themselves when shown
        if hasattr(frame, "on_show") and callable(getattr(frame, "on_show")):
            try:
                frame.on_show()
            except Exception as e:
                # Do not crash the router if the page's refresh fails
                messagebox.showerror("View Error", f"{name} failed to load:\n{e}")

        frame.tkraise()
        self._update_title_suffix(name)

    def safe_show(self, name: str):
        """
        Show frame only if the user is authenticated with YouTube (except Auth).

        Use this from other frames when navigating to pages that require an
        initialized YouTube client / valid session.
        """
        if name != "Auth" and not self.youtube_client:
            messagebox.showwarning(
                "Not Signed In",
                "You must sign in with your Google account first."
            )
            self.show_frame("Auth")
            return
        self.show_frame(name)

    def _update_title_suffix(self, name: str):
        """
        Show page and user in window title for clarity.
        """
        user = (
            self.session.channel_title
            or self.session.google_email
            or "Not signed in"
        )
        self.title(f"{self.TITLE} — {name} ({user})")

    # === SESSION / CLIENT MANAGEMENT =======================================

    def set_youtube_client(
        self,
        client: object,
        *,
        google_email: Optional[str] = None,
        channel_title: Optional[str] = None,
        channel_id: Optional[str] = None,
    ):
        """
        Called by your AuthFrame (or wherever you handle OAuth) once
        authentication succeeds.

        This wires the external YouTube client + basic profile info
        into the central App + Session.
        """
        self.youtube_client = client

        if google_email is not None:
            self.session.google_email = google_email
        if channel_title is not None:
            self.session.channel_title = channel_title
        if channel_id is not None:
            self.session.channel_id = channel_id

        # Refresh window title after login
        self._update_title_suffix("Auth")

    def clear_session(self):
        """
        Optional helper: logout-like behavior.
        Frames can call this when user presses "Sign out".
        """
        self.youtube_client = None
        self.session = Session()
        self.show_frame("Auth")

    # === LIFECYCLE =========================================================

    def on_close(self):
        """
        Cleanup hook for when the window is closed.
        If you later add files, background threads, etc., clean them up here.
        """
        self.destroy()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
