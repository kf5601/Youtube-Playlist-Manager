import tkinter as tk
from tkinter import ttk, messagebox


class HomePage(ttk.Frame):
    """
    Home screen for the YouTube Playlist Manager.

    Responsibilities (UI-level for now):
      - Show "Sign in with Google" / OAuth login button
      - After login, show:
          * Remaining API quota (placeholder label for now)
          * A tab that lists all playlists (placeholder treeview for now)
    """

    def __init__(self, master: tk.Misc, controller=None, **kwargs):
        """
        `controller` is optional, in case later you want to pass
        the main App object for navigation/state sharing.
        For now you can ignore it.
        """
        super().__init__(master, **kwargs)
        self.controller = controller

        # internal state placeholders
        self.is_logged_in = False
        self.current_user_label = tk.StringVar(value="Not signed in")
        self.quota_label_var = tk.StringVar(value="Remaining quota: —")
        self.status_label_var = tk.StringVar(value="Please sign in to view your playlists.")

        self._build_ui()

    def _build_ui(self) -> None:
        """Create all widgets and layout for the home page."""
        # === Title ===
        title = ttk.Label(self, text="YouTube Playlist Manager", style="Title.TLabel")
        title.pack(pady=(16, 8))

        # === Top bar: login + user status ===
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=16, pady=(0, 8))

        self.login_button = ttk.Button(
            top_bar,
            text="Sign in with Google",
            command=self.on_login_clicked
        )
        self.login_button.pack(side="left")

        user_info_label = ttk.Label(
            top_bar,
            textvariable=self.current_user_label
        )
        user_info_label.pack(side="left", padx=(12, 0))

        # Optional future: add a "Sign out" button
        # self.logout_button = ttk.Button(top_bar, text="Sign out", command=self.on_logout_clicked)
        # self.logout_button.pack(side="right")

        # === Notebook (tabs) ===
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # --- Overview tab ---
        overview_tab = ttk.Frame(notebook)
        notebook.add(overview_tab, text="Overview")

        quota_frame = ttk.LabelFrame(overview_tab, text="API Quota")
        quota_frame.pack(fill="x", padx=12, pady=(12, 8))

        quota_label = ttk.Label(quota_frame, textvariable=self.quota_label_var)
        quota_label.pack(anchor="w", padx=8, pady=8)

        status_frame = ttk.LabelFrame(overview_tab, text="Status")
        status_frame.pack(fill="x", padx=12, pady=(0, 12))

        status_label = ttk.Label(status_frame, textvariable=self.status_label_var)
        status_label.pack(anchor="w", padx=8, pady=8)

        # --- Playlists tab ---
        playlists_tab = ttk.Frame(notebook)
        notebook.add(playlists_tab, text="Playlists")

        playlists_frame = ttk.LabelFrame(playlists_tab, text="Your Playlists")
        playlists_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Treeview to show playlists: name, item count, maybe privacy
        columns = ("title", "item_count", "privacy")
        self.playlists_tree = ttk.Treeview(
            playlists_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
        )
        self.playlists_tree.pack(fill="both", expand=True, side="left", padx=(8, 0), pady=8)

        self.playlists_tree.heading("title", text="Title")
        self.playlists_tree.heading("item_count", text="Items")
        self.playlists_tree.heading("privacy", text="Privacy")

        self.playlists_tree.column("title", width=360, anchor="w")
        self.playlists_tree.column("item_count", width=80, anchor="center")
        self.playlists_tree.column("privacy", width=100, anchor="center")

        # Scrollbar for playlists
        scrollbar = ttk.Scrollbar(
            playlists_frame,
            orient="vertical",
            command=self.playlists_tree.yview
        )
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        self.playlists_tree.configure(yscrollcommand=scrollbar.set)

        # Bottom bar in playlists tab for "Open playlist" etc.
        actions_frame = ttk.Frame(playlists_tab)
        actions_frame.pack(fill="x", padx=12, pady=(0, 12))

        self.open_playlist_button = ttk.Button(
            actions_frame,
            text="Open selected playlist",
            command=self.on_open_playlist_clicked
        )
        self.open_playlist_button.pack(side="right")

        # At the start, disable playlist-related controls until login
        self._set_logged_out_state()

    # ======================================================================
    # State & UI helpers
    # ======================================================================

    def _set_logged_out_state(self) -> None:
        """Update widgets to reflect 'not signed in' state."""
        self.is_logged_in = False
        self.current_user_label.set("Not signed in")
        self.quota_label_var.set("Remaining quota: —")
        self.status_label_var.set("Please sign in to view your playlists.")
        self.open_playlist_button.state(["disabled"])
        # Clear playlists tree
        for row in self.playlists_tree.get_children():
            self.playlists_tree.delete(row)

    def _set_logged_in_state(self, user_display_name: str) -> None:
        """Update widgets to reflect 'signed in' state (dummy for now)."""
        self.is_logged_in = True
        self.current_user_label.set(f"Signed in as: {user_display_name}")
        self.status_label_var.set("Connected to YouTube. Playlists loaded.")
        self.open_playlist_button.state(["!disabled"])

    # ======================================================================
    # Event handlers (placeholders for now)
    # ======================================================================

    def on_login_clicked(self) -> None:
        """
        Handle "Sign in with Google".
        Right now this is just a placeholder that fakes a successful login.
        Later you’ll:
          - run the OAuth flow
          - get credentials / YouTube client
          - fetch remaining quota and playlists
          - update the UI based on that data
        """
        # TODO: replace with real OAuth logic
        messagebox.showinfo(
            "Login",
            "TODO: Implement OAuth login with Google here.\n"
            "For now, this just fakes a successful login."
        )

        # Fake logged-in state for UI testing
        fake_user = "demo.user@gmail.com"
        self._set_logged_in_state(user_display_name=fake_user)

        # Fake playlists data so you can see the UI
        self._load_demo_playlists()

        # Fake quota
        self.quota_label_var.set("Remaining quota: 10,000 units (demo)")

    def _load_demo_playlists(self) -> None:
        """
        Temporary helper: insert some fake playlists to visualize UI.
        Replace this later with real API data.
        """
        for row in self.playlists_tree.get_children():
            self.playlists_tree.delete(row)

        demo_data = [
            ("Watch Later", 42, "Private"),
            ("Favourites", 15, "Private"),
            ("Cybersecurity Tutorials", 23, "Unlisted"),
            ("Music Mix", 87, "Public"),
        ]
        for title, count, privacy in demo_data:
            self.playlists_tree.insert(
                "",
                "end",
                values=(title, count, privacy)
            )

    def on_open_playlist_clicked(self) -> None:
        """
        Handle "Open selected playlist".
        For now this just shows which playlist is selected.
        Later, you'll:
          - get the selected playlist's ID (from real API data)
          - navigate to a dedicated playlist page/frame
          - pass that playlist info to it
        """
        selected = self.playlists_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a playlist first.")
            return

        values = self.playlists_tree.item(selected[0], "values")
        playlist_title = values[0] if values else "(unknown)"

        # TODO: replace this with navigation to PlaylistPage or similar
        messagebox.showinfo(
            "Open Playlist",
            f"TODO: Open playlist page for:\n\n{playlist_title}"
        )

    # ======================================================================
    # Optional: hook called by app when this frame is shown
    # ======================================================================

    def on_show(self) -> None:
        """
        If your App calls `home.on_show()` when shown, you can use this
        to refresh data. For now it's a no-op.
        """
        # e.g., later: if logged in, refresh quota/playlists
        pass
