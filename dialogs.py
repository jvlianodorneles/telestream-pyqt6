import io
import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QLineEdit, QHBoxLayout, QGroupBox
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import qrcode

def get_icon_path(theme_name, icon_name):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "themes", "icons", theme_name, icon_name)

class AboutDialog(QDialog):
    def __init__(self, theme_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About/Donate")
        self.theme_name = theme_name
        self.layout = QVBoxLayout(self)

        # PIX Group
        pix_group = QGroupBox("PIX Donation")
        pix_layout = QVBoxLayout()
        pix_layout.setContentsMargins(10, 15, 10, 10)
        
        self.qr_label = QLabel()
        qr_hbox = QHBoxLayout()
        qr_hbox.addStretch()
        qr_hbox.addWidget(self.qr_label)
        qr_hbox.addStretch()
        pix_layout.addLayout(qr_hbox)

        self.generate_and_display_qr_code()
        pix_group.setLayout(pix_layout)
        self.layout.addWidget(pix_group)

        # Other Donations Group
        other_donations_group = QGroupBox("Other Donations")
        other_donations_layout = QVBoxLayout()
        other_donations_layout.setContentsMargins(10, 15, 10, 10)
        donation_label = QLabel('Enjoying the app? Consider sending a collectible gift on Telegram: <a href="https://t.me/jvlianodorneles">https://t.me/jvlianodorneles</a>.')
        donation_label.setOpenExternalLinks(True)
        donation_label.setWordWrap(True)
        donation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        other_donations_layout.addWidget(donation_label)
        other_donations_group.setLayout(other_donations_layout)
        self.layout.addWidget(other_donations_group)

        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(10, 15, 10, 10)
        self.back_button = QPushButton(QIcon(get_icon_path(self.theme_name, "go-previous.svg")), "Back")
        self.back_button.setToolTip("Return to the main window.")
        self.back_button.clicked.connect(self.accept)
        actions_layout.addWidget(self.back_button)
        actions_group.setLayout(actions_layout)
        self.layout.addWidget(actions_group)

        self.setMinimumWidth(400)

    def generate_and_display_qr_code(self):
        pix_string = "00020126580014br.gov.bcb.pix0136aa97cd56-b793-4c39-94be-c190a29f40865204000053039865802BR5925JULIANO_DORNELES_DOS_SANT6012Santo_Angelo610998803-41762290525C7X00138965117602953262656304D7E8"
        fill = "#f0f0f0" if self.theme_name == "dark" else "black"
        back = "transparent" if self.theme_name == "dark" else "white"

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=4)
        qr.add_data(pix_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill, back_color=back)
        
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        qt_image = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qt_image)
        self.qr_label.setPixmap(pixmap)
        self.qr_label.setFixedSize(pixmap.size())

class LogDialog(QDialog):
    log_cleared = pyqtSignal()

    def __init__(self, log_history, theme_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Log")
        self.theme_name = theme_name
        self.layout = QVBoxLayout(self)

        # Log Group
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(10, 15, 10, 10)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setToolTip("Displays application logs.")
        for message in log_history:
            self.log_viewer.append(message)
        log_layout.addWidget(self.log_viewer)
        log_group.setLayout(log_layout)
        self.layout.addWidget(log_group)

        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(10, 15, 10, 10)
        
        self.clear_button = QPushButton(QIcon(get_icon_path(self.theme_name, "edit-clear.svg")), "Clear Log")
        self.clear_button.setToolTip("Clear the log content.")
        self.clear_button.clicked.connect(self.log_cleared.emit)
        actions_layout.addWidget(self.clear_button)

        actions_layout.addStretch()

        self.back_button = QPushButton(QIcon(get_icon_path(self.theme_name, "go-previous.svg")), "Back")
        self.back_button.setToolTip("Return to the main window.")
        self.back_button.clicked.connect(self.accept)
        actions_layout.addWidget(self.back_button)
        actions_group.setLayout(actions_layout)
        self.layout.addWidget(actions_group)
        
        self.setMinimumSize(600, 400)

    def add_log_message(self, message):
        self.log_viewer.append(message)

class FavoritesDialog(QDialog):
    def __init__(self, favorites, theme_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Favorites")
        self.favorites = favorites
        self.theme_name = theme_name
        self.layout = QVBoxLayout(self)

        # Favorites List Group
        list_group = QGroupBox("Favorites List")
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(10, 15, 10, 10)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "URL", "Key"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setToolTip("List of your favorite servers. Click to select one for editing.")
        list_layout.addWidget(self.table)
        list_group.setLayout(list_layout)
        self.layout.addWidget(list_group)

        # Form Group
        form_group = QGroupBox("Add/Edit Favorite")
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(10, 15, 10, 10)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Server Name")
        self.name_input.setToolTip("A unique name for this favorite server.")
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)

        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Server URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("rtmps://...")
        self.url_input.setToolTip("The RTMP/RTMPS URL of the server.")
        url_layout.addWidget(self.url_input)
        form_layout.addLayout(url_layout)

        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Stream Key:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("secret_key")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setToolTip("Your unique stream key.")
        key_layout.addWidget(self.key_input)
        self.toggle_password_button = QPushButton("")
        self.toggle_password_button.setToolTip("Show/Hide the stream key.")
        key_layout.addWidget(self.toggle_password_button)
        form_layout.addLayout(key_layout)
        form_group.setLayout(form_layout)
        self.layout.addWidget(form_group)

        # Actions Group
        actions_group = QGroupBox("Actions")
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(10, 15, 10, 10)
        self.add_button = QPushButton("Add")
        self.add_button.setToolTip("Add a new favorite server.")
        buttons_layout.addWidget(self.add_button)
        self.edit_button = QPushButton("Save Edit")
        self.edit_button.setToolTip("Save changes to the selected favorite.")
        buttons_layout.addWidget(self.edit_button)
        self.remove_button = QPushButton("Remove")
        self.remove_button.setToolTip("Remove the selected favorite.")
        buttons_layout.addWidget(self.remove_button)
        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.setToolTip("Clear all input fields.")
        buttons_layout.addWidget(self.clear_button)
        self.back_button = QPushButton("Back")
        self.back_button.setToolTip("Return to the main window.")
        buttons_layout.addWidget(self.back_button)
        actions_group.setLayout(buttons_layout)
        self.layout.addWidget(actions_group)

        self.load_favorites_to_table()
        self.update_icons()

        # Connect signals
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.add_button.clicked.connect(self.add_favorite)
        self.edit_button.clicked.connect(self.edit_favorite)
        self.remove_button.clicked.connect(self.remove_favorite)
        self.clear_button.clicked.connect(self.clear_fields)
        self.back_button.clicked.connect(self.accept)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)

        self.setMinimumWidth(600)

    def update_icons(self):
        self.add_button.setIcon(QIcon(get_icon_path(self.theme_name, "list-add.svg")))
        self.edit_button.setIcon(QIcon(get_icon_path(self.theme_name, "document-save.svg")))
        self.remove_button.setIcon(QIcon(get_icon_path(self.theme_name, "list-remove.svg")))
        self.clear_button.setIcon(QIcon(get_icon_path(self.theme_name, "edit-clear.svg")))
        self.back_button.setIcon(QIcon(get_icon_path(self.theme_name, "go-previous.svg")))
        self.toggle_password_visibility(update_only=True)

    def load_favorites_to_table(self):
        self.table.setRowCount(0)
        for fav in self.favorites:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(fav["name"]))
            self.table.setItem(row_position, 1, QTableWidgetItem(fav["url"]))
            self.table.setItem(row_position, 2, QTableWidgetItem(fav["key"][:10] + "..."))

    def on_table_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.clear_fields()
            return
        
        selected_row = selected_rows[0].row()
        name = self.table.item(selected_row, 0).text()
        
        for fav in self.favorites:
            if fav["name"] == name:
                self.name_input.setText(fav["name"])
                self.url_input.setText(fav["url"])
                self.key_input.setText(fav["key"])
                break

    def add_favorite(self):
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        key = self.key_input.text().strip()

        if not name or not url or not key:
            QMessageBox.critical(self, "Error", "All fields (Name, URL, Key) are required.")
            return

        if any(fav["name"] == name for fav in self.favorites):
            QMessageBox.critical(self, "Error", f"A favorite with the name '{name}' already exists.")
            return

        self.favorites.append({"name": name, "url": url, "key": key})
        self.load_favorites_to_table()
        self.clear_fields()

    def edit_favorite(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        selected_row = selected_rows[0].row()
        original_name = self.table.item(selected_row, 0).text()

        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        key = self.key_input.text().strip()

        if not name or not url or not key:
            QMessageBox.critical(self, "Error", "All fields (Name, URL, Key) are required.")
            return

        if name != original_name and any(fav["name"] == name for fav in self.favorites):
            QMessageBox.critical(self, "Error", f"Another favorite with the name '{name}' already exists.")
            return

        for i, fav in enumerate(self.favorites):
            if fav["name"] == original_name:
                self.favorites[i] = {"name": name, "url": url, "key": key}
                break
        
        self.load_favorites_to_table()
        self.clear_fields()

    def remove_favorite(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        selected_row = selected_rows[0].row()
        name = self.table.item(selected_row, 0).text()

        self.favorites[:] = [fav for fav in self.favorites if fav["name"] != name]
        self.load_favorites_to_table()
        self.clear_fields()

    def clear_fields(self):
        self.name_input.clear()
        self.url_input.clear()
        self.key_input.clear()
        self.table.clearSelection()

    def toggle_password_visibility(self, update_only=False):
        if not update_only:
            is_password = self.key_input.echoMode() == QLineEdit.EchoMode.Password
            if is_password:
                self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            else:
                self.key_input.setEchoMode(QLineEdit.EchoMode.Password)

        if self.key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.toggle_password_button.setIcon(QIcon(get_icon_path(self.theme_name, "eye-hide.svg")))
            self.toggle_password_button.setToolTip("Show password.")
        else:
            self.toggle_password_button.setIcon(QIcon(get_icon_path(self.theme_name, "eye-show.svg")))
            self.toggle_password_button.setToolTip("Hide password.")