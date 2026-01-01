# ui/home.py
import tkinter as tk
from tkinter import ttk, messagebox

from youtube_client import YouTubeClient
from ui.playlist_window import PlaylistWindow


class HomePage(ttk.Frame):
    """
    Home screen:
      - Sign in with Google (OAuth)
      - Display estimated quota usage (session only)
      - List playlists
      - Open selected playlist in a new window
    """

    def __init__(self, master: tk.Misc, **kwargs):
        super().__init__(master, **kwargs)

        self.youtube_client: YouTubeClient | None = None
        self.playlists: list[dict] = []

        self.current_user_label = tk.StringVar(value="Not signed in")
        self.quota_label_var = tk.StringVar(value="Quota used this session: 0 units")
        self.status_label_var = tk.StringVar(value="Please sign in to view your playlists.")

        self._build_ui()

    def _build_ui(self) -> None:
        # Title
        title = ttk.Label(self, text="YouTube Playlist Manager", style="Title.TLabel")
        title.pack(pady=(16, 8))

        # Top bar
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=16, pady=(0, 8))

        self.login_button = ttk.Button(
            top_bar, text="Sign in with Google", command=self.on_login_clicked
        )
        self.login_button.pack(side="left")

        user_info_label = ttk.Label(top_bar, textvariable=self.current_user_label)
        user_info_label.pack(side="left", padx=(12, 0))

        # Notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Overview tab
        overview_tab = ttk.Frame(notebook)
        notebook.add(overview_tab, text="Overview")

        quota_frame = ttk.LabelFrame(overview_tab, text="Quota (Approximate)")
        quota_frame.pack(fill="x", padx=12, pady=(12, 8))

        quota_label = ttk.Label(quota_frame, textvariable=self.quota_label_var)
        quota_label.pack(anchor="w", padx=8, pady=4)

        note_label = ttk.Label(
            quota_frame,
            text="Note: Google does not expose exact remaining quota via the API.\n"
                 "This shows estimated usage (units) in this app session only.",
            wraplength=600,
        )
        note_label.pack(anchor="w", padx=8, pady=(0, 8))

        status_frame = ttk.LabelFrame(overview_tab, text="Status")
        status_frame.pack(fill="x", padx=12, pady=(0, 12))

        status_label = ttk.Label(status_frame, textvariable=self.status_label_var)
        status_label.pack(anchor="w", padx=8, pady=8)

        # Playlists tab
        playlists_tab = ttk.Frame(notebook)
        notebook.add(playlists_tab, text="Playlists")

        playlists_frame = ttk.LabelFrame(playlists_tab, text="Your Playlists")
        playlists_frame.pack(fill="both", expand=True, padx=12, pady=12)

        columns = ("title", "item_count", "privacy")
        self.playlists_tree = ttk.Treeview(
            playlists_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
        )
        self.playlists_tree.pack(
            fill="both", expand=True, side="left", padx=(8, 0), pady=8
        )

        self.playlists_tree.heading("title", text="Title")
        self.playlists_tree.heading("item_count", text="Items")
        self.playlists_tree.heading("privacy", text="Privacy")

        self.playlists_tree.column("title", width=360, anchor="w")
        self.playlists_tree.column("item_count", width=80, anchor="center")
        self.playlists_tree.column("privacy", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(
            playlists_frame, orient="vertical", command=self.playlists_tree.yview
        )
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)
        self.playlists_tree.configure(yscrollcommand=scrollbar.set)

        actions_frame = ttk.Frame(playlists_tab)
        actions_frame.pack(fill="x", padx=12, pady=(0, 12))

        self.open_playlist_button = ttk.Button(
            actions_frame,
            text="Open selected playlist",
            command=self.on_open_playlist_clicked,
            state="disabled",
        )
        self.open_playlist_button.pack(side="right")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_quota_label(self) -> None:
        if self.youtube_client:
            used = self.youtube_client.quota_used_units
            self.quota_label_var.set(f"Quota used this session: {used} units")

    def _load_playlists_into_tree(self) -> None:
        for row in self.playlists_tree.get_children():
            self.playlists_tree.delete(row)

        for pl in self.playlists:
            title = pl.get("title") or "(no title)"
            count = pl.get("item_count") or 0
            privacy = (pl.get("privacy_status") or "").capitalize()
            iid = pl["id"]  # use playlist ID as internal item id
            self.playlists_tree.insert(
                "",
                "end",
                iid=iid,
                values=(title, count, privacy),
            )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_login_clicked(self) -> None:
        """
        Handle "Sign in with Google".
        """
        try:
            self.status_label_var.set("Signing in...")
            self.update_idletasks()

            client = YouTubeClient()
            client.authenticate()

            info = client.get_channel_basic_info()
            channel_title = info.get("title") or "Unknown channel"
            self.youtube_client = client

            self.current_user_label.set(f"Signed in as: {channel_title}")
            self.status_label_var.set("Fetching playlists...")
            self.update_idletasks()

            self.playlists = client.list_playlists()
            self._load_playlists_into_tree()

            self.status_label_var.set("Playlists loaded.")
            self.open_playlist_button.config(state="normal")

            self._update_quota_label()

        except FileNotFoundError as e:
            messagebox.showerror(
                "OAuth Error",
                f"{e}\n\nMake sure client_secret.json is in the project folder.",
            )
            self.status_label_var.set("Sign-in failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sign in or load playlists:\n\n{e}")
            self.status_label_var.set("Sign-in failed.")

    def on_open_playlist_clicked(self) -> None:
        """
        Open the selected playlist in a new playlist window.
        """
        if not self.youtube_client:
            messagebox.showwarning("Not signed in", "Please sign in first.")
            return

        selected = self.playlists_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a playlist first.")
            return

        playlist_id = selected[0]
        playlist = next((p for p in self.playlists if p["id"] == playlist_id), None)
        if not playlist:
            messagebox.showerror("Error", "Could not find playlist details.")
            return

        # Open a new window for playlist management
        PlaylistWindow(
            master=self.winfo_toplevel(),
            youtube_client=self.youtube_client,
            playlist=playlist,
            all_playlists=self.playlists,
        )

        # Update quota estimate after actions in child window
        self._update_quota_label()
