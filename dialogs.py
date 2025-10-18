import io
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QLineEdit, QHBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import qrcode
from config import _

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("About/Donate"))
        self.layout = QVBoxLayout(self)

        # PIX QR Code
        pix_label = QLabel(_("PIX:"))
        pix_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(pix_label)
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.qr_label)
        self.generate_and_display_qr_code()

        # Donation message
        donation_label = QLabel(_('\nEnjoying the app? Consider sending a collectible gift on Telegram: <a href="https://t.me/jvlianodorneles">https://t.me/jvlianodorneles</a>'))
        donation_label.setOpenExternalLinks(True)
        donation_label.setWordWrap(True)
        donation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(donation_label)

        # Back button
        self.back_button = QPushButton(_("⬅️ Back"))
        self.back_button.clicked.connect(self.accept)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def generate_and_display_qr_code(self):
        pix_string = "00020126580014br.gov.bcb.pix0136aa97cd56-b793-4c39-94be-c190a29f40865204000053039865802BR5925JULIANO_DORNELES_DOS_SANT6012Santo_Angelo610998803-41762290525C7X00138965117602953262656304D7E8"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(pix_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QPixmap
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        qt_image = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qt_image)
        self.qr_label.setPixmap(pixmap)
        self.qr_label.setFixedSize(pixmap.size())

class LogDialog(QDialog):
    def __init__(self, log_history, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Application Log"))
        self.layout = QVBoxLayout(self)

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        for message in log_history:
            self.log_viewer.append(message)
        self.layout.addWidget(self.log_viewer)

        self.back_button = QPushButton(_("⬅️ Back"))
        self.back_button.clicked.connect(self.accept)
        self.layout.addWidget(self.back_button)

    def add_log_message(self, message):
        self.log_viewer.append(message)

class FavoritesDialog(QDialog):
    def __init__(self, favorites, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Manage Favorites"))
        self.favorites = favorites
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([_("Name"), _("URL"), _("Key")])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        form_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_("Server Name"))
        form_layout.addWidget(QLabel(_("Name:")))
        form_layout.addWidget(self.name_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(_("rtmps://..."))
        form_layout.addWidget(QLabel(_("Server URL:")))
        form_layout.addWidget(self.url_input)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(_("secret_key"))
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(QLabel(_("Stream Key:")))
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_input)
        self.toggle_password_button = QPushButton(_("👁️ Show"))
        key_layout.addWidget(self.toggle_password_button)
        form_layout.addLayout(key_layout)

        self.layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton(_("➕ Add"))
        buttons_layout.addWidget(self.add_button)
        self.edit_button = QPushButton(_("💾 Save Edit"))
        buttons_layout.addWidget(self.edit_button)
        self.remove_button = QPushButton(_("🗑️ Remove"))
        buttons_layout.addWidget(self.remove_button)
        self.clear_button = QPushButton(_("🧹 Clear Fields"))
        buttons_layout.addWidget(self.clear_button)
        self.back_button = QPushButton(_("⬅️ Back"))
        buttons_layout.addWidget(self.back_button)
        self.layout.addLayout(buttons_layout)

        self.load_favorites_to_table()

        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.add_button.clicked.connect(self.add_favorite)
        self.edit_button.clicked.connect(self.edit_favorite)
        self.remove_button.clicked.connect(self.remove_favorite)
        self.clear_button.clicked.connect(self.clear_fields)
        self.back_button.clicked.connect(self.accept)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)

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
            QMessageBox.critical(self, _("Error"), _("All fields (Name, URL, Key) are required."))
            return

        if any(fav["name"] == name for fav in self.favorites):
            QMessageBox.critical(self, _("Error"), _(f"A favorite with the name '{name}' already exists."))
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
            QMessageBox.critical(self, _("Error"), _("All fields (Name, URL, Key) are required."))
            return

        if name != original_name and any(fav["name"] == name for fav in self.favorites):
            QMessageBox.critical(self, _("Error"), _(f"Another favorite with the name '{name}' already exists."))
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

    def toggle_password_visibility(self):
        if self.key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setText(_("🙈 Hide"))
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setText(_("👁️ Show"))