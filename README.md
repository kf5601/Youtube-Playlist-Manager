YouTube Playlist Manager (Tkinter + YouTube Data API)

A simple desktop GUI app (Tkinter) for managing your YouTube playlists using the **YouTube Data API v3**.

You can:
- Sign in with your Google account (OAuth 2.0, local desktop app)
- See your channel and playlists
- Open a playlist in a separate window to:
  - View videos in that playlist
  - Delete videos from the playlist
  - **Copy** videos to another playlist (original stays intact)
  - Search YouTube globally and add videos to the playlist

Everything runs **locally** on your machine. Each user brings their own Google Cloud project + OAuth credentials,
Features

- Desktop GUI (Tkinter, no browser UI required after login)
- OAuth login with Google (using your own `client_secret.json`)
- List all playlists for your YouTube account
- View videos inside a playlist
- Delete videos from a playlist
- Copy videos from one playlist to another
- Global YouTube search and add search results into a playlist
- Shows **approximate quota usage** in the current app session

> **Note:** Google does **not** provide an API endpoint to see your exact remaining daily quota.  
> This app only tracks an **estimated quota usage for this session** based on the documented unit costs of each API call.
> Google typically provides 10,000 quotas usage per day

Dependencies:
- Python 3.10+ (tested with Python 3.13)
- Tkinter (standard library)
- Google API Client libraries:
  - `google-api-python-client`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`

Project Structure
```text
YouTubePlayListAPI/
│
├─ app.py                     # Entry point. Creates main window and shows HomePage.
├─ youtube_client.py          # OAuth + YouTube API wrapper + quota estimation.
│
└─ ui/
   ├─ __init__.py             # Empty, marks ui as a Python package.
   ├─ home.py                 # HomePage: login, quota display, playlists list, open playlist window.
   └─ playlist_window.py      # PlaylistWindow: per-playlist management (videos + search).
└─ doc/
   └─ assets/                 # documentation images
```

---

## Setup – Google Cloud / OAuth
**Each user must set up their own Google Cloud project and credentials.**
### 1️⃣ Create a Google Cloud project

- Go to Google Cloud Console: https://console.cloud.google.com/

- Create a new project (or use an existing one).

### 2️⃣ Enable YouTube Data API v3

- In the Cloud Console, go to:

- APIs & Services → Library

- Search for YouTube Data API v3.

- Click Enable.

### 3️⃣ Configure OAuth consent screen

- APIs & Services → OAuth consent screen

- User type: choose External.

- Fill in:

  - App name: e.g. Local YouTube Playlist Manager

  - User support email: your email

  - Developer contact email: your email

- Save and continue.
- You don’t need full verification for local/testing use.

### 4️⃣ Add yourself as a Test User

- Still under OAuth consent screen:

  - Scroll down to Audience

  - Click `+ Add users`.

  - Add your Google account email(s).

  - Save.

- As long as the app is in Testing mode, only test users can log in.

### 5️⃣ Create OAuth credentials (Desktop app)

- Go to:

  - APIs & Services → Credentials

  - Click + CREATE CREDENTIALS → OAuth client ID

  - Application type: Desktop application

  - Name: anything (e.g. Local Desktop Client)

- Create → Download JSON file.

- Rename as `client_secrets.json` and save it into the project root as:

YouTubePlayListAPI/
├─ app.py
├─ youtube_client.py
├─ client_secrets.json    <-- put it here
├─ doc/
└─ ui/

⚠️ This client_secret.json is your private key for this app.
Keep it out of git and do not share it.

---

## Running the App
- From the project root run:
  - python app.py

- The app will open a Tkinter window:

- Click “Sign in with Google”

- A browser window will open:

  - Choose the test user account you whitelisted

  - Accept the permissions (YouTube Data API scopes)

- The app will:

  - Show your channel name

  - Fetch your playlists

  - Display approximate quota usage for this session
