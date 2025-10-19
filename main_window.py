import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QDialog, 
    QTableWidget, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent
from config import load_config, save_config, _
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

        # Load config
        self.config = load_config()
        self.favorites = self.config.get("favorites", [])
        self.current_theme = self.config.get("theme", "dark")
        self.apply_theme()

        # Streamer
        self.streamer = Streamer()
        self.streamer.log_message.connect(self.log_message)
        self.streamer.stream_started.connect(self.on_stream_started)
        self.streamer.stream_stopped.connect(self.on_stream_stopped)

        # Video Path
        self.layout.addWidget(QLabel(_("Video Path:")))
        video_path_layout = QHBoxLayout()
        self.video_path_input = QLineEdit()
        self.video_path_input.setPlaceholderText(_("e.g.: /home/user/video.mp4"))
        video_path_layout.addWidget(self.video_path_input)
        self.browse_button = QPushButton(_("📁 Browse..."))
        video_path_layout.addWidget(self.browse_button)
        self.layout.addLayout(video_path_layout)

        # YouTube URL
        self.layout.addWidget(QLabel(_("Or YouTube URL:")))
        self.youtube_url_input = QLineEdit()
        self.youtube_url_input.setPlaceholderText(_("e.g.: https://www.youtube.com/watch?v=..."))
        self.layout.addWidget(self.youtube_url_input)

        # Favorite Server
        self.layout.addWidget(QLabel(_("Favorite Server:")))
        self.favorite_server_select = QComboBox()
        self.layout.addWidget(self.favorite_server_select)

        # Server URL
        self.layout.addWidget(QLabel(_("Server URL (RTMP/RTMPS):")))
        self.server_url_input = QLineEdit()
        self.server_url_input.setPlaceholderText(_("e.g.: rtmps://dc1-1.rtmp.t.me/s/"))
        self.layout.addWidget(self.server_url_input)

        # Stream Key
        self.layout.addWidget(QLabel(_("Telegram Stream Key:")))
        stream_key_layout = QHBoxLayout()
        self.stream_key_input = QLineEdit()
        self.stream_key_input.setPlaceholderText(_("e.g.: 123456:abc-123"))
        self.stream_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        stream_key_layout.addWidget(self.stream_key_input)
        self.toggle_password_button = QPushButton(_("👁️ Show"))
        stream_key_layout.addWidget(self.toggle_password_button)
        self.layout.addLayout(stream_key_layout)

        # RPi Checkbox
        self.rpi_checkbox = QCheckBox(_("RPi"))
        self.layout.addWidget(self.rpi_checkbox)

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton(_("▶️ Start Stream"))
        self.start_button.setObjectName("start_button")
        action_buttons_layout.addWidget(self.start_button)
        self.stop_button = QPushButton(_("⏹️ Stop Stream"))
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setEnabled(False)
        action_buttons_layout.addWidget(self.stop_button)
        self.layout.addLayout(action_buttons_layout)

        # Utility Buttons
        utility_buttons_layout = QHBoxLayout()
        self.log_button = QPushButton(_("📜 Show Log"))
        utility_buttons_layout.addWidget(self.log_button)
        self.about_button = QPushButton(_("ℹ️ About/Donate"))
        utility_buttons_layout.addWidget(self.about_button)
        self.favorites_button = QPushButton(_("⭐ Manage Favorites"))
        utility_buttons_layout.addWidget(self.favorites_button)
        self.layout.addLayout(utility_buttons_layout)

        self.populate_favorites_dropdown()

        # Connect signals
        self.browse_button.clicked.connect(self.browse_file)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        self.video_path_input.textChanged.connect(self.video_path_changed)
        self.youtube_url_input.textChanged.connect(self.youtube_url_changed)
        self.favorite_server_select.currentIndexChanged.connect(self.favorite_selected)
        self.about_button.clicked.connect(self.show_about_dialog)
        self.log_button.clicked.connect(self.show_log_dialog)
        self.favorites_button.clicked.connect(self.show_favorites_dialog)
        self.start_button.clicked.connect(self.start_streaming)
        self.stop_button.clicked.connect(self.stop_streaming)

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
            # The application is running from a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # The application is running from a normal Python environment
            base_path = os.path.dirname(__file__)

        qss_file = os.path.join(base_path, f"themes/{self.current_theme}.qss")
        try:
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Theme file not found: {qss_file}")

    def browse_file(self):
        file_name, __ = QFileDialog.getOpenFileName(self, _("Select a video file"), "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if file_name:
            self.video_path_input.setText(file_name)

    def toggle_password_visibility(self):
        if self.stream_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.stream_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setText(_("🙈 Hide"))
        else:
            self.stream_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setText(_("👁️ Show"))

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
        self.favorite_server_select.addItem(_("Select a favorite"), None)
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
        dialog = AboutDialog(self)
        dialog.exec()

    def show_log_dialog(self):
        if not self.log_dialog:
            self.log_dialog = LogDialog(self.log_history, self)
        self.log_dialog.show()

    def show_favorites_dialog(self):
        dialog = FavoritesDialog(self.favorites, self)
        if dialog.exec():
            self.favorites = dialog.favorites
            self.config["favorites"] = self.favorites
            save_config(self.config)
            self.populate_favorites_dropdown()

    def log_message(self, message):
        self.log_history.append(message)
        if self.log_dialog:
            self.log_dialog.add_log_message(message)

    def start_streaming(self):
        video_path = self.video_path_input.text()
        youtube_url = self.youtube_url_input.text()
        server_url = self.server_url_input.text()
        stream_key = self.stream_key_input.text()
        is_rpi = self.rpi_checkbox.isChecked()

        if not (video_path or youtube_url) or not server_url or not stream_key:
            QMessageBox.critical(self, _("Error"), _("Server URL and stream key are required, plus a video path or YouTube URL."))
            return

        if video_path and not os.path.exists(video_path):
            QMessageBox.critical(self, _("Error"), _(f"File not found: {video_path}"))
            return

        selected_favorite = self.favorite_server_select.currentData()
        if selected_favorite:
            self.config["last_favorite_name"] = selected_favorite["name"]
        else:
            self.config.pop("last_favorite_name", None)
        save_config(self.config)

        stream_source = video_path if video_path else youtube_url
        
        # Run streaming in a separate thread
        self.stream_thread = QThread()
        self.streamer.moveToThread(self.stream_thread)
        self.stream_thread.started.connect(lambda: self.streamer.start_streaming(stream_source, server_url, stream_key, is_rpi))
        self.stream_thread.start()

    def stop_streaming(self):
        self.streamer.stop_streaming()

    def on_stream_started(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def on_stream_stopped(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if hasattr(self, 'stream_thread') and self.stream_thread.isRunning():
            self.stream_thread.quit()
            self.stream_thread.wait()

    def closeEvent(self, event):
        self.stop_streaming()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())