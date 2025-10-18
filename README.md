# TeleStream PyQt6

This is a simple application built in Python, to stream local video files or YouTube streams to a Telegram channel using `ffmpeg`.

## Features

-   Stream a local video file or a YouTube video.
-   Saves the last used favorite for convenience.
-   Displays basic status and error logs.
-   Buttons to start and stop streaming.
-   **Favorite Servers Management**: Add, edit, and remove favorite streaming servers (Name, URL, and Stream Key) for quick access.

<p align="center">
<img width="610" height="458" alt="pyqt61" src="https://github.com/user-attachments/assets/d724fa4a-a83e-45e5-b842-9161b8eaede0" />

<img width="698" height="524" alt="pyqt62" src="https://github.com/user-attachments/assets/b30dd60d-c7ce-451d-8c44-97ad816b420f" />
</p>

## Prerequisites

-   **Python 3.7+**
-   **ffmpeg**: You need to have `ffmpeg` installed and accessible in your system's `PATH`.
    -   For Debian/Ubuntu: `sudo apt update && sudo apt install ffmpeg`
    -   For Arch Linux: `sudo pacman -S ffmpeg`
    -   For macOS (using Homebrew): `brew install ffmpeg`

## Installation

1.  Clone this repository or download the files.
2.  Navigate to the project directory:
    ```bash
    cd telestream-pyqt6
    ```
3.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
4.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
5.  Install the necessary Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
6.  Run the application:
    ```bash
    python3 app.py
    ```

## How to Use

1.  Run the application:
    ```bash
    python3 app.py
    ```
2.  **Video Source**: You have two options for the video source, which are mutually exclusive:
    *   **Video Path**: Enter the absolute path to the local video file you want to stream (e.g., `/home/user/my_video.mp4`).
    *   **Or YouTube URL**: Paste the URL of the YouTube video you want to stream (e.g., `https://www.youtube.com/watch?v=...`).
3.  **Favorite Servers Management**:
    *   Click the "Manage Favorites" button to open the management screen.
    *   On this screen, you can add new favorite servers by providing a Name, the Server URL (e.g., `rtmps://dc1-1.rtmp.t.me/s/`), and the Stream Key.
    *   Select a favorite from the table to edit its details or remove it.
    *   Changes are automatically saved to `config.json`.
4.  **Server Selection**: On the main screen, use the "Favorite Server" dropdown to select one of your saved servers. The Server URL and Stream Key will be automatically filled.
5.  **Server URL**: This field will be automatically filled when selecting a favorite. You can also edit it manually if you are not using a favorite.
6.  **Stream Key**: This field will be automatically filled when selecting a favorite. You can also edit it manually if you are not using a favorite. The field hides the key for privacy.
7.  **Start Stream**: Press the "Start Stream" button to begin streaming.
8.  **Stop Stream**: Press the "Stop Stream" button to end the `ffmpeg` process. You can also exit the application with `Esc` and confirming the exit.
