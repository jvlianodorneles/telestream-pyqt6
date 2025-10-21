# TeleStream PyQt6

A simple application built in Python to stream local video files or YouTube videos to an RTMP server, such as Telegram, using `ffmpeg`.

## Features

-   **Video Sources**: Stream a local video file or a YouTube video.
-   **Favorite Servers**: Save, edit, and remove favorite streaming servers (Name, URL, and Stream Key) for quick access.
-   **Themeable Interface**: Switch between a light and dark theme to suit your preference.
-   **Loop Control**: Choose whether to play a video once or loop it infinitely. This works for both local files and YouTube streams.
-   **Quality Presets**: Select from various resolution and bitrate presets (1080p, 720p, 480p, or source quality) to manage your bandwidth and stream quality.
-   **Log Management**: View application and `ffmpeg` logs in a dedicated window, with options to clear the log or save it to a timestamped file.
-   **Hardware Acceleration (RPi)**: Includes a specific option for Raspberry Pi users to use the `h264_v4l2m2m` codec for hardware-accelerated video encoding.

<p align="center">
<img width="933" height="700" alt="pyqt61" src="https://github.com/user-attachments/assets/dc136e17-9b51-42c5-98ac-3549944186e0" />

<img width="836" height="627" alt="pyqt62" src="https://github.com/user-attachments/assets/fac15e40-e52c-42e4-8fff-89842c7fac8d" />
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

1.  **Video Source**:
    *   **Video Path**: Enter the absolute path to a local video file.
    *   **Or YouTube URL**: Paste the URL of a YouTube video.

2.  **Server Details**:
    *   **Favorite Server**: Select a pre-saved server from this dropdown to auto-fill the URL and Key.
    *   **Server URL**: The RTMP/RTMPS URL of the streaming server.
    *   **Stream Key**: Your private stream key. Click the eye icon to show/hide it.

3.  **Options**:
    *   **RPi Mode**: Check this to use the `h264_v4l2m2m` codec, recommended for hardware acceleration on Raspberry Pi.
    *   **Loop Mode**: Choose "Loop Infinitely" to repeat the video when it ends, or "Play Once" to stream it a single time.
    *   **Quality Preset**: Select a resolution and bitrate for your stream. "Source Quality" will not resize or re-encode the video bitrate.

4.  **Streaming**:
    *   Press **Start Stream** to begin.
    *   Press **Stop Stream** to end the transmission.

5.  **Utilities**:
    *   **Show Log**: Opens a window to view detailed logs from the application and `ffmpeg`. You can also clear the log from this window.
    *   **Save Log**: Saves the current log session to a timestamped `.txt` file in the application's root directory.
    *   **Manage Favorites**: Opens a dialog to add, edit, or remove your saved server configurations.
    *   **About/Donate**: Shows information about the application and donation options.
    *   **Toggle Theme**: Switches the application between light and dark themes.
