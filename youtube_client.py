# youtube_client.py
# more dependencies yay...
import os
import pickle
from typing import Optional, Dict, Any, List
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# download from Google Cloud Console its gonna have some numbers and letters behind "secret" you can change that if you want or change this to match
CLIENT_SECRET_FILE = "client_secrets.json"

# Scopes: full YouTube manage (needed for playlist CRUD + search)
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Quota cost (from YouTube Data API docs)
# this is subject to change, and usually they give 10,000 units per day
QUOTA_COST = {
    "playlists.list": 1,
    "playlistItems.list": 1,
    "playlistItems.insert": 50,
    "playlistItems.update": 50,
    "playlistItems.delete": 50,
    "search.list": 100,
}


class YouTubeClient:
    """
    Wraps OAuth + YouTube Data API calls.

    Tracks approximate quota usage *in this session* based on known costs.
    This is NOT the real "remaining quota" from Google (they don't expose it :\ ).
    """
    # SECURITY NOTE: this implementation stores OAuth tokens in a pickle file, which is not secure for shared environments. Use at your own risk and add to gitignore
    def __init__(self, token_file: str = "token.pickle") -> None:
        self.token_file = token_file
        self.creds = None
        self.service = None
        self.quota_used_units: int = 0  # session-only estimate

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> None:
        """
        Run (or reuse) OAuth flow and build the YouTube client.
        """
        creds = None

        # Try load existing token
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "rb") as token:
                    creds = pickle.load(token)
            except Exception:
                creds = None

        # Refresh if needed
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        # If still no valid creds, start new OAuth flow
        if not creds or not creds.valid:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    f"Missing {CLIENT_SECRET_FILE}. "
                    "Download it from the Google Cloud Console."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            # This opens browser, handles Google login & consent
            creds = flow.run_local_server(port=0)

            # Save credentials
            try:
                with open(self.token_file, "wb") as token:
                    pickle.dump(creds, token)
            except Exception:
                pass

        self.creds = creds
        self.service = build("youtube", "v3", credentials=creds)

    def is_authenticated(self) -> bool:
        return self.service is not None

    # ------------------------------------------------------------------
    # Helper: track quota
    # ------------------------------------------------------------------

    def _add_quota_usage(self, endpoint: str) -> None:
        self.quota_used_units += QUOTA_COST.get(endpoint, 0)

    # ------------------------------------------------------------------
    # Basic info (channel)
    # ------------------------------------------------------------------

    def get_channel_basic_info(self) -> Dict[str, Optional[str]]:
        """
        Get the user's channel ID and title.
        Returns a dict with keys: 'channel_id', 'title'.
        """
        if not self.service:
            raise RuntimeError("YouTube client is not authenticated.")

        self._add_quota_usage("playlists.list")  # close enough; channels.list is also 1

        resp = (
            self.service.channels()
            .list(part="snippet", mine=True)
            .execute()
        )
        items = resp.get("items", [])
        if not items:
            return {"channel_id": None, "title": None}
        ch = items[0]
        return {
            "channel_id": ch.get("id"),
            "title": ch.get("snippet", {}).get("title"),
        }

    # ------------------------------------------------------------------
    # Playlists
    # ------------------------------------------------------------------
    # change max_result as needed, but more than 50 playlist is crazy
    def list_playlists(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Return a list of playlists the user owns.
        Each item is a dict with keys: id, title, item_count, privacy_status.
        """
        if not self.service:
            raise RuntimeError("YouTube client is not authenticated.")

        self._add_quota_usage("playlists.list")

        playlists = []
        request = self.service.playlists().list(
            part="snippet,contentDetails,status",
            mine=True,
            maxResults=max_results,
        )

        while request is not None:
            resp = request.execute()
            for item in resp.get("items", []):
                playlists.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("snippet", {}).get("title"),
                        "item_count": item.get("contentDetails", {}).get("itemCount"),
                        "privacy_status": item.get("status", {}).get("privacyStatus"),
                    }
                )

            request = self.service.playlists().list_next(request, resp)

        return playlists

    # ------------------------------------------------------------------
    # Playlist items (videos in a playlist)
    # ------------------------------------------------------------------

    def list_playlist_items(
        self, playlist_id: str, max_results: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Return playlist items (videos) in a playlist.
        Each item has id (playlistItemId), video_id, title, position.
        """
        if not self.service:
            raise RuntimeError("YouTube client is not authenticated.")

        self._add_quota_usage("playlistItems.list")

        items: List[Dict[str, Any]] = []

        request = self.service.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=max_results,
        )

        while request is not None:
            resp = request.execute()
            for it in resp.get("items", []):
                snippet = it.get("snippet", {})
                content = it.get("contentDetails", {})
                items.append(
                    {
                        "playlist_item_id": it.get("id"),
                        "video_id": content.get("videoId"),
                        "title": snippet.get("title"),
                        "position": snippet.get("position"),
                    }
                )

            request = self.service.playlistItems().list_next(request, resp)

        return items

    # ------------------------------------------------------------------
    # CRUD on playlist items
    # ------------------------------------------------------------------

    def delete_playlist_item(self, playlist_item_id: str) -> None:
        if not self.service:
            raise RuntimeError("YouTube client is not authenticated.")

        self._add_quota_usage("playlistItems.delete")
        self.service.playlistItems().delete(id=playlist_item_id).execute()

    def insert_playlist_item(self, playlist_id: str, video_id: str) -> None:
        if not self.service:
            raise RuntimeError("YouTube client is not authenticated.")

        self._add_quota_usage("playlistItems.insert")
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            }
        }
        self.service.playlistItems().insert(part="snippet", body=body).execute()

    def move_playlist_item(
        self,
        source_playlist_item_id: str,
        source_playlist_id: str,
        target_playlist_id: str,
        video_id: str,
    ) -> None:
        """
        Simple "move": insert into target, then delete from source.
        """
        # Insert into target
        self.insert_playlist_item(target_playlist_id, video_id)
        # Delete from source
        self.delete_playlist_item(source_playlist_item_id)

    # ------------------------------------------------------------------
    # Search videos (global YouTube search)
    # ------------------------------------------------------------------

    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search YouTube (global) for videos by keyword.
        Each item has: video_id, title, channel_title.
        """
        if not self.service:
            raise RuntimeError("YouTube client is not authenticated.")

        self._add_quota_usage("search.list")

        resp = (
            self.service.search()
            .list(
                part="snippet",
                type="video",
                q=query,
                maxResults=max_results,
            )
            .execute()
        )
        results: List[Dict[str, Any]] = []
        for item in resp.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            results.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "channel_title": snippet.get("channelTitle"),
                }
            )
        return results
    
    # ------------------------------------------------------------------
    # Logout helper
    # ------------------------------------------------------------------
    def logout(self) -> None:
        """
        Logs out locally by deleting the cached token file and clearing in-memory client state.
        This does NOT log you out of Google in your browser; it just forces OAuth next time.
        """
        # Clear in-memory state
        self.creds = None
        self.service = None
        self.quota_used_units = 0
        # Delete cached token so OAuth is required next time
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
        except Exception:
            # Not fatal; user can still manually delete it
            pass

