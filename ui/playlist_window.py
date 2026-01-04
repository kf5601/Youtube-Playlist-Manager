# ui/playlist_window.py
# dependencies
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

from youtube_client import YouTubeClient


class PlaylistWindow(tk.Toplevel):
    """
    A separate window that manages a single playlist:
      - List videos in the playlist
      - Delete from playlist
      - Copy (add) to another playlist
      - Search YouTube and add to this playlist
    """

    def __init__(
        self,
        master: tk.Misc,
        youtube_client: YouTubeClient,
        playlist: Dict[str, Any],
        all_playlists: List[Dict[str, Any]],
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.youtube_client = youtube_client
        self.playlist = playlist
        self.all_playlists = all_playlists

        self.title(f"Playlist: {playlist.get('title', '(no title)')}")
        # Bigger default window so buttons are visible without resizing
        self.geometry("1920x1080")
        self.minsize(1000, 650)

        self.videos: List[Dict[str, Any]] = []
        self.search_results: List[Dict[str, Any]] = []

        self._build_ui()
        self._load_playlist_items()

    def _build_ui(self) -> None:
        # Top label
        header = ttk.Label(
            self,
            text=f"Playlist: {self.playlist.get('title', '(no title)')}",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(pady=(10, 5))

        # Main paned window: left = playlist videos, right = search
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # ------------------------------------------------------------------
        # Left side: playlist videos
        # ------------------------------------------------------------------
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=3)

        lf_label = ttk.Label(left_frame, text="Videos in this playlist")
        lf_label.pack(anchor="w", pady=(0, 4))

        self.videos_tree = ttk.Treeview(
            left_frame,
            columns=("title", "video_id", "position"),
            show="headings",
            selectmode="browse",
        )
        self.videos_tree.heading("title", text="Title")
        self.videos_tree.heading("video_id", text="Video ID")
        self.videos_tree.heading("position", text="Pos")

        self.videos_tree.column("title", width=350, anchor="w")
        self.videos_tree.column("video_id", width=200, anchor="center")
        self.videos_tree.column("position", width=50, anchor="center")

        self.videos_tree.pack(fill="both", expand=True, side="left")

        vsb = ttk.Scrollbar(
            left_frame, orient="vertical", command=self.videos_tree.yview
        )
        vsb.pack(side="right", fill="y")
        self.videos_tree.configure(yscrollcommand=vsb.set)

        # Buttons under playlist videos
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill="x", pady=(6, 0))

        self.delete_button = ttk.Button(
            buttons_frame, text="Delete from playlist", command=self.on_delete_clicked
        )
        self.delete_button.pack(side="left", padx=(0, 4))

        # Dropdown for "Copy to playlist"
        ttk.Label(buttons_frame, text="Copy to:").pack(side="left")
        self.target_playlist_var = tk.StringVar(value="")
        playlist_titles = [
            f"{pl.get('title', '(no title)')} ({pl['id']})"
            for pl in self.all_playlists
            if pl["id"] != self.playlist["id"]
        ]
        self.target_menu = ttk.Combobox(
            buttons_frame,
            textvariable=self.target_playlist_var,
            values=playlist_titles,
            state="readonly",
            width=40,
        )
        self.target_menu.pack(side="left", padx=4)

        self.move_button = ttk.Button(
            buttons_frame, text="Copy video", command=self.on_move_clicked
        )
        self.move_button.pack(side="left", padx=(4, 0))

        # ------------------------------------------------------------------
        # Right side: search & add
        # ------------------------------------------------------------------
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        search_label = ttk.Label(
            right_frame, text="Search YouTube (global) and add to this playlist"
        )
        search_label.pack(anchor="w", pady=(0, 4))

        search_bar = ttk.Frame(right_frame)
        search_bar.pack(fill="x", pady=(0, 4))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)

        search_button = ttk.Button(
            search_bar, text="Search", command=self.on_search_clicked
        )
        search_button.pack(side="left", padx=(4, 0))

        # Reminder label about quota cost
        quota_hint = ttk.Label(
            right_frame,
            text="Note: each global search costs about 100 quota units.",
            foreground="gray"
        )
        quota_hint.pack(anchor="w", pady=(0, 4))

        self.search_tree = ttk.Treeview(
            right_frame,
            columns=("title", "video_id", "channel"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.search_tree.heading("title", text="Title")
        self.search_tree.heading("video_id", text="Video ID")
        self.search_tree.heading("channel", text="Channel")

        self.search_tree.column("title", width=280, anchor="w")
        self.search_tree.column("video_id", width=160, anchor="center")
        self.search_tree.column("channel", width=150, anchor="w")

        self.search_tree.pack(fill="both", expand=True, side="left")

        s_vsb = ttk.Scrollbar(
            right_frame, orient="vertical", command=self.search_tree.yview
        )
        s_vsb.pack(side="right", fill="y")
        self.search_tree.configure(yscrollcommand=s_vsb.set)

        add_button = ttk.Button(
            right_frame, text="Add selected to playlist", command=self.on_add_clicked
        )
        add_button.pack(pady=(6, 0))

    # ------------------------------------------------------------------
    # Load / refresh data
    # ------------------------------------------------------------------

    def _load_playlist_items(self) -> None:
        """Fetch videos from YouTube and show them in the left table."""
        try:
            self.videos = self.youtube_client.list_playlist_items(self.playlist["id"])
            self._refresh_videos_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlist items:\n\n{e}")

    def _refresh_videos_tree(self) -> None:
        for row in self.videos_tree.get_children():
            self.videos_tree.delete(row)

        for item in self.videos:
            pid = item["playlist_item_id"]
            title = item.get("title") or "(no title)"
            vid = item.get("video_id") or ""
            pos = item.get("position") if item.get("position") is not None else ""
            self.videos_tree.insert(
                "",
                "end",
                iid=pid,
                values=(title, vid, pos),
            )

    # ------------------------------------------------------------------
    # Event handlers - playlist side
    # ------------------------------------------------------------------

    def on_delete_clicked(self) -> None:
        selected = self.videos_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a video to delete.")
            return

        playlist_item_id = selected[0]

        if not messagebox.askyesno(
            "Confirm delete",
            "Remove this video from the playlist?",
        ):
            return

        try:
            self.youtube_client.delete_playlist_item(playlist_item_id)
            # reload
            self._load_playlist_items()
            messagebox.showinfo("Deleted", "Video removed from playlist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete:\n\n{e}")

    def on_move_clicked(self) -> None:
        """
        Copy a video to another playlist (does NOT delete from original).
        """
        selected = self.videos_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a video to copy.")
            return

        chosen = self.target_playlist_var.get()
        if not chosen:
            messagebox.showwarning("No target", "Choose a target playlist to copy to.")
            return

        # chosen format: "Title (playlist_id)"
        if "(" not in chosen or not chosen.endswith(")"):
            messagebox.showerror("Error", "Unexpected playlist selection format.")
            return

        target_playlist_id = chosen.split("(")[-1].rstrip(")").strip()

        playlist_item_id = selected[0]
        item = next(
            (v for v in self.videos if v["playlist_item_id"] == playlist_item_id),
            None,
        )
        if not item:
            messagebox.showerror("Error", "Could not find selected video details.")
            return

        video_id = item["video_id"]

        if not messagebox.askyesno(
            "Confirm copy",
            f"Copy video '{item.get('title', '(no title)')}'\n"
            f"to playlist ID {target_playlist_id} ?\n\n"
            f"(It will remain in the original playlist.)",
        ):
            return

        try:
            # Only insert into target; leave original alone
            self.youtube_client.insert_playlist_item(target_playlist_id, video_id)
            # We keep current playlist items as-is (no reload needed here),
            # but you could reload if you want to keep positions updated.
            messagebox.showinfo("Copied", "Video copied to target playlist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy video:\n\n{e}")

    # ------------------------------------------------------------------
    # Event handlers - search side
    # ------------------------------------------------------------------

    def on_search_clicked(self) -> None:
        """
        Handle global YouTube search. This costs ~100 units of quota,
        so we show a warning before actually calling the API.
        """
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty search", "Enter a search query first.")
            return

        # Quota warning: search.list costs about 100 units per call
        proceed = messagebox.askyesno(
            "Quota Warning",
            "Global YouTube search uses about 100 quota units per search.\n"
            "Google's default YouTube Data API quota is around 10,000 units per day,\n"
            "so frequent searches can quickly burn through your daily limit.\n\n"
            "Do you want to continue with this search?"
        )
        if not proceed:
            return

        try:
            self.search_results = self.youtube_client.search_videos(query)
            self._refresh_search_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Search failed:\n\n{e}")

    def _refresh_search_tree(self) -> None:
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)

        for idx, item in enumerate(self.search_results):
            video_id = item["video_id"]
            title = item.get("title") or "(no title)"
            channel = item.get("channel_title") or ""
            iid = f"sr_{idx}_{video_id}"
            self.search_tree.insert(
                "",
                "end",
                iid=iid,
                values=(title, video_id, channel),
            )

    def on_add_clicked(self) -> None:
        selected = self.search_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a search result to add.")
            return

        item_id = selected[0]
        node = self.search_tree.item(item_id)
        _, video_id, _ = node["values"]

        try:
            self.youtube_client.insert_playlist_item(self.playlist["id"], video_id)
            self._load_playlist_items()
            messagebox.showinfo("Added", "Video added to playlist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add video:\n\n{e}")
