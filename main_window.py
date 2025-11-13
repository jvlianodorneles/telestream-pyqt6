
import sys
import os
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
    QFileDialog, QMessageBox, QCheckBox, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import QThread, Qt, QSize
from PyQt6.QtGui import QKeyEvent, QIcon
from config import load_config, save_config
from dialogs import AboutDialog, LogDialog, FavoritesDialog
from streamer import Streamer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TeleStream")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.log_history = []
        self.log_dialog = None
        self.last_stream_info = {}
        self.user_stopped_stream = False
        self.streamer = None
        self.stream_thread = None

        # Load config
        self.config = load_config()
        self.favorites = self.config.get("favorites", [])
        self.current_theme = self.config.get("theme", "dark")

        # --- UI Setup ---
        self._init_ui()
        self.live_story_checkbox.setChecked(self.config.get("live_story", False))
        self.apply_theme() # Apply theme and icons

    def _init_ui(self):
        # --- Source Group ---
        source_group = QGroupBox("Source")
        source_layout = QVBoxLayout()
        source_layout.setContentsMargins(10, 15, 10, 10)

        video_path_layout = QHBoxLayout()
        self.video_path_input = QLineEdit()
        self.video_path_input.setPlaceholderText("e.g.: /home/user/video.mp4")
        self.video_path_input.setToolTip("Path to the local video file.")
        video_path_layout.addWidget(QLabel("Video Path:"))
        video_path_layout.addWidget(self.video_path_input)
        self.browse_button = QPushButton("")
        self.browse_button.setToolTip("Browse for a video file.")
        video_path_layout.addWidget(self.browse_button)
        source_layout.addLayout(video_path_layout)

        youtube_url_layout = QHBoxLayout()
        self.youtube_url_input = QLineEdit()
        self.youtube_url_input.setPlaceholderText("e.g.: https://www.youtube.com/watch?v=...")
        self.youtube_url_input.setToolTip("URL of the YouTube video.")
        youtube_url_layout.addWidget(QLabel("Or YouTube URL:"))
        youtube_url_layout.addWidget(self.youtube_url_input)
        source_layout.addLayout(youtube_url_layout)
        
        source_group.setLayout(source_layout)
        self.layout.addWidget(source_group)

        # --- Server Group ---
        server_group = QGroupBox("Server")
        server_layout = QVBoxLayout()
        server_layout.setContentsMargins(10, 15, 10, 10)

        favorite_server_layout = QHBoxLayout()
        self.favorite_server_select = QComboBox()
        self.favorite_server_select.setToolTip("Select a favorite server.")
        favorite_server_layout.addWidget(QLabel("Favorite Server:"))
        favorite_server_layout.addWidget(self.favorite_server_select)
        favorite_server_layout.addStretch()
        server_layout.addLayout(favorite_server_layout)

        server_url_layout = QHBoxLayout()
        self.server_url_input = QLineEdit()
        self.server_url_input.setPlaceholderText("e.g.: rtmps://dc1-1.rtmp.t.me/s/")
        self.server_url_input.setToolTip("RTMP/RTMPS server URL.")
        server_url_layout.addWidget(QLabel("Server URL:"))
        server_url_layout.addWidget(self.server_url_input)
        server_layout.addLayout(server_url_layout)

        stream_key_layout = QHBoxLayout()
        self.stream_key_input = QLineEdit()
        self.stream_key_input.setPlaceholderText("e.g.: 123456:abc-123")
        self.stream_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.stream_key_input.setToolTip("Your Telegram stream key.")
        stream_key_layout.addWidget(QLabel("Stream Key:"))
        stream_key_layout.addWidget(self.stream_key_input)
        self.toggle_password_button = QPushButton("")
        self.toggle_password_button.setToolTip("Show/Hide the stream key.")
        stream_key_layout.addWidget(self.toggle_password_button)
        server_layout.addLayout(stream_key_layout)

        server_group.setLayout(server_layout)
        self.layout.addWidget(server_group)

        # --- Options Group ---
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(10, 15, 10, 10)

        rpi_layout = QHBoxLayout()
        self.rpi_checkbox = QCheckBox("RPi Mode")
        self.rpi_checkbox.setToolTip("Use the h264_v4l2m2m codec for streaming on a Raspberry Pi.")
        rpi_layout.addWidget(self.rpi_checkbox)
        rpi_layout.addStretch()
        options_layout.addLayout(rpi_layout)

        live_story_layout = QHBoxLayout()
        self.live_story_checkbox = QCheckBox("Live Story (9:16)")
        self.live_story_checkbox.setToolTip("Create a 9:16 output with a blurred background for vertical streaming.")
        live_story_layout.addWidget(self.live_story_checkbox)
        live_story_layout.addStretch()
        options_layout.addLayout(live_story_layout)

        loop_layout = QHBoxLayout()
        loop_layout.addWidget(QLabel("Loop Mode:"))
        self.loop_mode_select = QComboBox()
        self.loop_mode_select.addItems(["Loop Infinitely", "Play Once"])
        self.loop_mode_select.setToolTip("Choose how the video source should be handled when it ends.")
        loop_layout.addWidget(self.loop_mode_select)
        loop_layout.addStretch()
        options_layout.addLayout(loop_layout)

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality Preset:"))
        self.quality_preset_select = QComboBox()
        self.quality_preset_select.addItems([
            "Source Quality",
            "1080p (5 Mbps)",
            "720p (3 Mbps)",
            "480p (1.5 Mbps)"
        ])
        self.quality_preset_select.setToolTip("Choose the resolution and bitrate for the stream.")
        quality_layout.addWidget(self.quality_preset_select)
        quality_layout.addStretch()
        options_layout.addLayout(quality_layout)

        options_group.setLayout(options_layout)
        self.layout.addWidget(options_group)

        # --- Actions Group ---
        actions_group = QGroupBox("Actions")
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setContentsMargins(10, 15, 10, 10)
        self.start_button = QPushButton("Start Stream")
        self.start_button.setObjectName("start_button")
        self.start_button.setToolTip("Start the stream.")
        self.start_button.setIconSize(QSize(32, 32))
        action_buttons_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop Stream")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setToolTip("Stop the stream.")
        self.stop_button.setEnabled(False)
        self.stop_button.setIconSize(QSize(32, 32))
        action_buttons_layout.addWidget(self.stop_button)
        actions_group.setLayout(action_buttons_layout)
        self.layout.addWidget(actions_group)

        # --- Utility Buttons ---
        utility_buttons_layout = QHBoxLayout()
        self.log_button = QPushButton("Show Log")
        self.log_button.setToolTip("Show the application log.")
        utility_buttons_layout.addWidget(self.log_button)
        self.save_log_button = QPushButton("Save Log")
        self.save_log_button.setToolTip("Save the application log to a file.")
        utility_buttons_layout.addWidget(self.save_log_button)
        self.favorites_button = QPushButton("Manage Favorites")
        self.favorites_button.setToolTip("Manage favorite servers.")
        utility_buttons_layout.addWidget(self.favorites_button)
        self.about_button = QPushButton("About/Donate")
        self.about_button.setToolTip("About the application.")
        utility_buttons_layout.addWidget(self.about_button)
        self.theme_button = QPushButton("")
        self.theme_button.setObjectName("theme_button")
        self.theme_button.setToolTip("Toggle light/dark theme.")
        self.theme_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        utility_buttons_layout.addWidget(self.theme_button)
        self.layout.addLayout(utility_buttons_layout)

        self.populate_favorites_dropdown()

        # --- Icon Mapping ---
        self.icon_map = {
            self.browse_button: "document-open.svg",
            self.start_button: "media-playback-start.svg",
            self.stop_button: "media-playback-stop.svg",
            self.log_button: "view-list-text.svg",
            self.save_log_button: "document-save.svg",
            self.favorites_button: "emblem-favorite.svg",
            self.about_button: "help-about.svg",
        }

        # --- Connect signals ---
        self.live_story_checkbox.toggled.connect(self.live_story_toggled)
        self.browse_button.clicked.connect(self.browse_file)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        self.video_path_input.textChanged.connect(self.video_path_changed)
        self.youtube_url_input.textChanged.connect(self.youtube_url_changed)
        self.favorite_server_select.currentIndexChanged.connect(self.favorite_selected)
        self.about_button.clicked.connect(self.show_about_dialog)
        self.log_button.clicked.connect(self.show_log_dialog)
        self.save_log_button.clicked.connect(self.save_log_to_file)
        self.favorites_button.clicked.connect(self.show_favorites_dialog)
        self.start_button.clicked.connect(self.start_streaming)
        self.stop_button.clicked.connect(self.stop_streaming)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.setMinimumWidth(600)

    def live_story_toggled(self, checked):
        self.quality_preset_select.setEnabled(not checked)
        if checked:
            self.quality_preset_select.setToolTip("Quality is automatically set for Live Story mode.")
        else:
            self.quality_preset_select.setToolTip("Choose the resolution and bitrate for the stream.")

    def get_icon_path(self, icon_name):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, "themes", "icons", self.current_theme, icon_name)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_D:
            self.toggle_theme()

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        self.config["theme"] = self.current_theme
        save_config(self.config)
        self.apply_theme()

    def apply_theme(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        qss_file = os.path.join(base_path, f"themes/{self.current_theme}.qss")
        try:
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Theme file not found: {qss_file}")
        
        # Update icons
        for button, icon_name in self.icon_map.items():
            button.setIcon(QIcon(self.get_icon_path(icon_name)))
        
        if self.current_theme == "dark":
            self.theme_button.setIcon(QIcon(self.get_icon_path("weather-clear.svg")))
        else:
            self.theme_button.setIcon(QIcon(self.get_icon_path("weather-clear-night.svg")))

        self.toggle_password_visibility(update_only=True) # Update eye icon

    def browse_file(self):
        file_name, __ = QFileDialog.getOpenFileName(self, "Select a video file", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if file_name:
            self.video_path_input.setText(file_name)

    def toggle_password_visibility(self, update_only=False):
        if not update_only:
            is_password = self.stream_key_input.echoMode() == QLineEdit.EchoMode.Password
            if is_password:
                self.stream_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            else:
                self.stream_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        if self.stream_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.toggle_password_button.setIcon(QIcon(self.get_icon_path("eye-hide.svg")))
        else:
            self.toggle_password_button.setIcon(QIcon(self.get_icon_path("eye-show.svg")))

    def video_path_changed(self, text):
        if text:
            self.youtube_url_input.clear()
            self.youtube_url_input.setEnabled(False)
        else:
            self.youtube_url_input.setEnabled(True)

    def youtube_url_changed(self, text):
        if text:
            self.video_path_input.clear()
            self.video_path_input.setEnabled(False)
            self.browse_button.setEnabled(False)
        else:
            self.video_path_input.setEnabled(True)
            self.browse_button.setEnabled(True)

    def populate_favorites_dropdown(self):
        self.favorite_server_select.clear()
        self.favorite_server_select.addItem("Select a favorite", None)
        for fav in self.favorites:
            self.favorite_server_select.addItem(fav["name"], fav)
        
        last_fav_name = self.config.get("last_favorite_name")
        if last_fav_name:
            index = self.favorite_server_select.findText(last_fav_name)
            if index != -1:
                self.favorite_server_select.setCurrentIndex(index)
                self.favorite_selected(index)

    def favorite_selected(self, index):
        favorite = self.favorite_server_select.itemData(index)
        if favorite:
            self.server_url_input.setText(favorite["url"])
            self.stream_key_input.setText(favorite["key"])
            self.config["last_favorite_name"] = favorite["name"]
            save_config(self.config)
        else:
            self.server_url_input.clear()
            self.stream_key_input.clear()

    def show_about_dialog(self):
        dialog = AboutDialog(self.current_theme, self)
        dialog.exec()

    def show_log_dialog(self):
        if not self.log_dialog:
            self.log_dialog = LogDialog(self.log_history, self.current_theme, self)
            self.log_dialog.finished.connect(self.on_log_dialog_finished)
            self.log_dialog.log_cleared.connect(self.on_log_cleared)
        self.log_dialog.show()
        self.log_dialog.activateWindow()

    def on_log_dialog_finished(self):
        self.log_dialog = None

    def on_log_cleared(self):
        self.log_history.clear()
        if self.log_dialog:
            self.log_dialog.log_viewer.clear()

    def save_log_to_file(self):
        if not self.log_history:
            QMessageBox.information(self, "Info", "Log is empty. Nothing to save.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"telestream_log_{timestamp}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log_history))
            QMessageBox.information(self, "Success", f"Log successfully saved to {filename}")
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Failed to save log file: {e}")

    def show_favorites_dialog(self):
        dialog = FavoritesDialog(self.favorites, self.current_theme, self)
        if dialog.exec():
            self.favorites = dialog.favorites
            self.config["favorites"] = self.favorites
            save_config(self.config)
            self.populate_favorites_dropdown()

    def log_message(self, message):
        self.log_history.append(message)
        if self.log_dialog:
            self.log_dialog.add_log_message(message)

    def start_streaming(self, from_loop=False):
        if not from_loop:
            self.user_stopped_stream = False
            video_path = self.video_path_input.text()
            youtube_url = self.youtube_url_input.text()
            server_url = self.server_url_input.text()
            stream_key = self.stream_key_input.text()
            is_rpi = self.rpi_checkbox.isChecked()
            loop_mode = self.loop_mode_select.currentText()
            quality_preset = self.quality_preset_select.currentText()
            is_live_story = self.live_story_checkbox.isChecked()

            self.config["live_story"] = is_live_story
            save_config(self.config)

            if not (video_path or youtube_url) or not server_url or not stream_key:
                QMessageBox.critical(self, "Error", "Server URL and stream key are required, plus a video path or YouTube URL.")
                return
            
            if video_path and not os.path.exists(video_path):
                QMessageBox.critical(self, "Error", f"File not found: {video_path}")
                return

            stream_source = video_path if video_path else youtube_url
            
            self.last_stream_info = {
                "source": stream_source,
                "server_url": server_url,
                "stream_key": stream_key,
                "is_rpi": is_rpi,
                "loop_mode": loop_mode,
                "quality_preset": quality_preset,
                "is_live_story": is_live_story
            }

            selected_favorite = self.favorite_server_select.currentData()
            if selected_favorite:
                self.config["last_favorite_name"] = selected_favorite["name"]
            else:
                self.config.pop("last_favorite_name", None)
            save_config(self.config)

        self.start_button.setEnabled(False)

        # Use stored info for re-looping
        info = self.last_stream_info
        
        self.streamer = Streamer()
        self.stream_thread = QThread()

        self.streamer.log_message.connect(self.log_message)
        self.streamer.stream_started.connect(self.on_stream_started)
        self.streamer.stream_stopped.connect(self.on_stream_stopped)
        self.streamer.stream_stopped.connect(self.stream_thread.quit)
        
        self.streamer.moveToThread(self.stream_thread)
        self.stream_thread.started.connect(lambda: self.streamer.start_streaming(
            info["source"], info["server_url"], info["stream_key"], 
            info["is_rpi"], info["loop_mode"], info["quality_preset"],
            info["is_live_story"]
        ))
        
        self.stream_thread.finished.connect(self.on_thread_finished)
        self.stream_thread.finished.connect(self.streamer.deleteLater)
        self.stream_thread.finished.connect(self.stream_thread.deleteLater)
        
        self.stream_thread.start()

    def stop_streaming(self):
        self.user_stopped_stream = True
        if self.streamer:
            self.stop_button.setEnabled(False)
            self.streamer.stop_streaming()

    def on_stream_started(self):
        self.stop_button.setEnabled(True)

    def on_stream_stopped(self):
        # This is called when the process inside the thread stops.
        # The thread itself is still finishing.
        pass

    def on_thread_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.streamer = None
        self.stream_thread = None

        # Re-looping logic
        if not self.user_stopped_stream and self.last_stream_info:
            is_youtube = self.last_stream_info["source"].startswith("http")
            if is_youtube and self.last_stream_info["loop_mode"] == "Loop Infinitely":
                self.log_message("Re-looping YouTube stream...")
                self.start_streaming(from_loop=True)

    def closeEvent(self, event):
        self.stop_streaming()
        super().closeEvent(event)