import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import sys
print("Importing PySide6...")
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

print("Importing local modules...")
from src.core.api_client import ApiClient
from src.services.auth_service import AuthService
from src.viewmodels.login_viewmodel import LoginViewModel
from src.views.login_view import LoginView
from utils import load_styles, icon
print("All imports completed.")


def main():
    app = QApplication(sys.argv)
    
    # Force Fusion style and Light Palette to ignore macOS/Windows Dark Mode
    app.setStyle(QStyleFactory.create("Fusion"))
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 250, 252))
    palette.setColor(QPalette.WindowText, QColor(15, 23, 42))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(241, 245, 249))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, QColor(15, 23, 42))
    palette.setColor(QPalette.Text, QColor(15, 23, 42))
    palette.setColor(QPalette.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(15, 23, 42))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(37, 99, 235))
    palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)
    
    app.setWindowIcon(icon("src/resources/images/app.ico"))

    load_styles(app)

    api_client = ApiClient()
    auth_service = AuthService(api_client)
    login_vm = LoginViewModel(auth_service)

    view = LoginView(login_vm)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
