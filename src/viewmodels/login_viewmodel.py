from PySide6.QtCore import QObject, Signal
from src.services.auth_service import AuthService


class LoginViewModel(QObject):
    login_success = Signal(dict)
    login_error = Signal(str)
    loading_changed = Signal(bool)

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service

    def login(self, email: str, password: str):
        self.loading_changed.emit(True)
        try:
            result = self.auth_service.login(email, password)
            self.login_success.emit(result)
        except Exception as e:
            self.login_error.emit(str(e))
        finally:
            self.loading_changed.emit(False)
