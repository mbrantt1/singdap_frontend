from src.core.api_client import ApiClient


class AuthService:
    def __init__(self, api_client: ApiClient):
        self.api = api_client

    def login(self, email: str, password: str) -> dict:
        return self.api.post(
            "/auth/login",
            {
                "email": email,
                "password": password
            }
        )
