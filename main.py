import sys
from PySide6.QtWidgets import QApplication

from src.core.api_client import ApiClient
from src.services.auth_service import AuthService
from src.viewmodels.login_viewmodel import LoginViewModel
from src.views.login_view import LoginView


def main():
    app = QApplication(sys.argv)

    load_styles(app)
    
    api_client = ApiClient()
    auth_service = AuthService(api_client)
    login_vm = LoginViewModel(auth_service)

    view = LoginView(login_vm)
    view.show()

    sys.exit(app.exec())


def load_styles(app):
    with open("src/resources/styles.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())


if __name__ == "__main__":
    main()
