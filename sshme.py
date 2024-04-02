import subprocess
import sys
import os
import json
import pyperclip
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QHBoxLayout,  QLineEdit, QPushButton, \
    QListWidget, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QFileDialog, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon, QCursor
import shutil


class AddEditCredentialDialog(QDialog):
    def __init__(self, parent=None, credential=None):
        super().__init__(parent)
        self.setWindowTitle('Add/Edit Credential')

        # Widgets
        self.alias_edit = QLineEdit()
        self.ip_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.keyfile_edit = QLineEdit()
        self.keyfile_button = QPushButton('Browse')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        # Layout
        layout = QFormLayout()
        layout.addRow("Alias:", self.alias_edit)
        layout.addRow("IP:", self.ip_edit)
        layout.addRow("Username:", self.username_edit)
        keyfile_layout = QHBoxLayout()
        keyfile_layout.addWidget(self.keyfile_edit)
        keyfile_layout.addWidget(self.keyfile_button)
        layout.addRow("Keyfile Path:", keyfile_layout)
        layout.addRow("Password:", self.password_edit)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        self.setLayout(layout)

        # Set initial values if editing existing credential
        if credential:
            self.alias_edit.setText(credential.get('alias', ''))
            self.ip_edit.setText(credential.get('ip', ''))
            self.username_edit.setText(credential.get('username', ''))
            self.keyfile_edit.setText(credential.get('keyfile', ''))
            self.password_edit.setText(credential.get('password', ''))

        # Connect signals
        self.keyfile_button.clicked.connect(self.browse_keyfile)

    def browse_keyfile(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("All files (*.*)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.keyfile_edit.setText(file_path)

    def get_credential(self):
        alias = self.alias_edit.text()
        ip = self.ip_edit.text()
        username = self.username_edit.text()
        keyfile = self.keyfile_edit.text()
        password = self.password_edit.text()
        return {'alias': alias, 'ip': ip, 'username': username, 'keyfile': keyfile, 'password': password}


class ManageCredentialsDialog(QDialog):
    def __init__(self, credentials):
        super().__init__()
        self.setWindowTitle("Manage Credentials")
        self.credentials = credentials

        self.list_widget = QListWidget()
        self.populate_list_widget()

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_credential)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_credential)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(remove_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def populate_list_widget(self):
        self.list_widget.clear()
        for credential in self.credentials:
            self.list_widget.addItem(credential['alias'])

    def edit_credential(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            selected_index = self.list_widget.row(selected_item)
            credential = self.credentials[selected_index]
            dialog = AddEditCredentialDialog(credential=credential)
            if dialog.exec_():
                updated_credential = dialog.get_credential()
                self.credentials[selected_index] = updated_credential
                self.populate_list_widget()

    def remove_credential(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            selected_index = self.list_widget.row(selected_item)
            del self.credentials[selected_index]
            self.populate_list_widget()


class PreferencesDialog(QDialog):
    def __init__(self, ssh_app, parent=None):
        super().__init__(parent)
        self.ssh_app = ssh_app
        self.setWindowTitle('Preferences')

        # Widgets
        self.terminal_combo = QComboBox()
        self.terminal_combo.addItems(["x-terminal-emulator", "gnome-terminal", "konsole", "xterm", "rxvt"])

        terminal_preference = self.ssh_app.preferences.get('terminal', 'x-terminal-emulator')
        index = self.terminal_combo.findText(terminal_preference)
        if index >= 0:
            self.terminal_combo.setCurrentIndex(index)

        self.export_button = QPushButton('Export Credentials')
        self.import_button = QPushButton('Import Credentials')

        # Layout
        layout = QFormLayout()
        layout.addRow("Terminal:", self.terminal_combo)
        layout.addRow(self.export_button)
        layout.addRow(self.import_button)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        self.setLayout(layout)

        # Connect signals
        self.export_button.clicked.connect(self.export_credentials)
        self.import_button.clicked.connect(self.import_credentials)

    def accept(self):
        terminal = self.terminal_combo.currentText()
        self.ssh_app.preferences['terminal'] = terminal
        self.ssh_app.save_preferences()
        super().accept()

    def export_credentials(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, 'w') as f:
                json.dump(self.ssh_app.credentials, f, indent=4)

    def import_credentials(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, 'r') as f:
                self.ssh_app.credentials = json.load(f)
            self.ssh_app.save_credentials()


class SSHCredentialsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SSH Credentials')
        self.credentials = []
        self.preferences = {}
        self.load_credentials()
        self.load_preferences()

        self.tray_icon = QSystemTrayIcon(QIcon('sshme-logo.png'), self)
        self.tray_icon.setToolTip('SSH Credentials')
        self.tray_icon.activated.connect(self.tray_icon_activated)

        self.tray_menu = QMenu(self)
        self.create_tray_menu_items()

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def create_tray_menu_items(self):
        for credential in self.credentials:
            action = self.tray_menu.addAction(credential['alias'])
            action.triggered.connect(lambda checked, cred=credential: self.connect_ssh(cred))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction('Add Credential', self.add_credential)
        self.tray_menu.addAction('Manage Credentials', self.manage_credentials)
        self.tray_menu.addAction('Preferences', self.open_preferences)
        self.tray_menu.addAction('About', self.about)
        self.tray_menu.addAction('Quit', self.quit)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.tray_menu.exec_(QCursor.pos())

    def open_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec_()

    def manage_credentials(self):
        dialog = ManageCredentialsDialog(self.credentials)
        dialog.exec_()
        self.save_credentials()
        self.create_tray_menu_items()  # Update tray menu

    def about(self):
        QMessageBox.about(self, "About SSH Credentials Manager",
                          "SSH Credentials Manager\n\n"
                          "A simple system tray application for managing SSH credentials.\n\n"
                          "Developed by: Aakash Poudel\n"
                          "GitHub: https://github.com/akashpoudelnp\n"
                          "License: MIT")

    def quit(self):
        self.quit()

    def add_credential(self):
        dialog = AddEditCredentialDialog()
        if dialog.exec_():
            new_credential = dialog.get_credential()
            self.credentials.append(new_credential)
            self.save_credentials()
            self.create_tray_menu_items()  # Update tray menu

    def connect_ssh(self, credential):
        ip, username, keyfile, password = credential['ip'], credential['username'], credential['keyfile'], credential[
            'password']

        # Construct the SSH command
        ssh_command = f"ssh {username}@{ip}"

        # If a keyfile is provided, add it to the SSH command
        if keyfile:
            ssh_command += f" -i {keyfile}"

        # Launch the selected terminal with the SSH command
        terminal = self.preferences.get('terminal', 'x-terminal-emulator')

        # Check if terminal is installed
        if not shutil.which(terminal):
            QMessageBox.critical(None, 'Error',
                                 f'Terminal "{terminal}" not found, please select a installed terminal from preferences.')
            return

        subprocess.Popen([terminal, '-e', ssh_command])

        # Copy password to clipboard
        if password:
            pyperclip.copy(password)

    def load_preferences(self):
        # Load preferences from config directory
        config_dir = os.path.join(os.path.expanduser('~'), '.ssh_credentials_manager')
        config_file = os.path.join(config_dir, 'preferences.json')

        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.preferences = json.load(f)

    def save_preferences(self):
        # Save preferences to config directory
        config_dir = os.path.join(os.path.expanduser('~'), '.ssh_credentials_manager')
        config_file = os.path.join(config_dir, 'preferences.json')
        with open(config_file, 'w') as f:
            json.dump(self.preferences, f, indent=4)

    def load_credentials(self):
        # Load credentials from config directory
        config_dir = os.path.join(os.path.expanduser('~'), '.ssh_credentials_manager')
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, 'credentials.json')

        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.credentials = json.load(f)

    def save_credentials(self):
        # Save credentials to config directory
        config_dir = os.path.join(os.path.expanduser('~'), '.ssh_credentials_manager')
        config_file = os.path.join(config_dir, 'credentials.json')
        with open(config_file, 'w') as f:
            json.dump(self.credentials, f, indent=4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ssh_app = SSHCredentialsApp()
    app.exec_()
