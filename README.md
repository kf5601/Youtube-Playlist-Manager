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
- OAuth login with Google (using your own `client_secrets.json`)
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
    - <img width="2559" height="1403" alt="1" src="https://github.com/user-attachments/assets/b90c0345-7935-4b50-83a6-b8572aeccd89" />


- Search for YouTube Data API v3.
    - <img width="2553" height="1404" alt="2" src="https://github.com/user-attachments/assets/b457f4bd-3668-4dbd-96bf-d4232c580126" />


- Click Enable.

### 3️⃣ Configure OAuth consent screen

- APIs & Services → OAuth consent screen
    - <img width="2560" height="1404" alt="3" src="https://github.com/user-attachments/assets/fdc93b72-fd1a-4063-8d29-55e24d1cd258" />


- User type: choose External.
    - <img width="2556" height="1401" alt="4" src="https://github.com/user-attachments/assets/60522fed-85f8-4f7d-b2f2-7c9eeeb11aef" />


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
      - <img width="2558" height="1402" alt="5" src="https://github.com/user-attachments/assets/f3b5ab05-d5ba-4094-b138-1bf8db0477bf" />


  - Add your Google account email(s).

  - Save.

- As long as the app is in Testing mode, only test users can log in.

### 5️⃣ Create OAuth credentials (Desktop app)

- Go to:

  - APIs & Services → Credentials
      - <img width="2558" height="1404" alt="6" src="https://github.com/user-attachments/assets/b0c424b2-e0db-40d3-8d9f-27d9837f77e3" />


  - Click + CREATE CREDENTIALS → OAuth client ID
      - <img width="2557" height="1400" alt="7" src="https://github.com/user-attachments/assets/a2efd0a9-8c07-4904-a835-eaa0e47e240b" />


  - Application type: Desktop app
      - <img width="584" height="404" alt="8" src="https://github.com/user-attachments/assets/f20cd3ef-4137-4380-bda0-04e58202868b" />


  - Name: anything (e.g. Local Desktop Client)

- Create → Download JSON file.
    - <img width="511" height="646" alt="9" src="https://github.com/user-attachments/assets/ec5b5f29-0ad1-4114-93c6-390d4bd65aab" />



- Rename as `client_secrets.json` and save it into the project root as:
```
YouTubePlayListAPI/
├─ app.py
├─ youtube_client.py
├─ client_secrets.json    <-- put it here
├─ doc/
└─ ui/
```
<img width="653" height="334" alt="10" src="https://github.com/user-attachments/assets/5bf4756c-18ee-477f-b358-12ab2b081263" />


⚠️ This client_secrets.json is your private key for this app.
Keep it out of git and do not share it.

---

## Running the App
- From the project root run:
  - python app.py

- The app will open a Tkinter window:

- Click “Sign in with Google”
  - <img width="1920" height="1108" alt="11" src="https://github.com/user-attachments/assets/a9c85ff7-98c7-4bcf-8d67-224f23fd05b1" />


- A browser window will open:

  - Choose the test user account you whitelisted

  - Accept the permissions (YouTube Data API scopes)

- The app will:

  - Show your channel name

  - Fetch your playlists

  - Display approximate quota usage for this session
