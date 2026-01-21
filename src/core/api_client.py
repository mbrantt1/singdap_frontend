import requests
from src.config.settings import API_BASE_URL


class ApiClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None

    def set_token(self, token: str):
        self.token = token

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ===============================
    # GET
    # ===============================
    def get(self, path: str):
        url = f"{self.base_url}{path}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    # ===============================
    # POST
    # ===============================
    def post(self, path: str, data: dict):
        url = f"{self.base_url}{path}"
        response = requests.post(
            url,
            json=data,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    # ===============================
    # DELETE
    # ===============================
    
    def delete(self, endpoint):
        r = requests.delete(self.base_url + endpoint)
        r.raise_for_status()
        return r.json() if r.content else None
    
    # ===============================
    # PUT 
    # ===============================
    def put(self, endpoint: str, payload: dict):
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
