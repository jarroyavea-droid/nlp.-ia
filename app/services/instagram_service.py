import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
BASE_URL = "https://graph.facebook.com/v21.0"

class InstagramService:
    def __init__(self):
        self.token = ACCESS_TOKEN
        self.business_id = BUSINESS_ACCOUNT_ID
        print(f"InstagramService inicializado con cuenta ID: {self.business_id}")

    def _make_request(self, method, endpoint, params=None):
        """Método auxiliar para hacer peticiones y mostrar el error real de Facebook."""
        url = f"{BASE_URL}/{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.token
        
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, params=params)
            
        if response.status_code != 200:
            print(f"\nERROR DETALLADO DE FACEBOOK API:")
            print(f"URL intentada: {url}")
            print(f"Respuesta de Facebook: {response.json()}")  # <--- ESTO NOS DIRÁ LA VERDAD
            response.raise_for_status()
            
        return response.json()

    def get_media(self, fields="id,caption,comments_count", limit=25):
        endpoint = f"{self.business_id}/media"
        params = {"fields": fields, "limit": limit}
        return self._make_request("GET", endpoint, params).get("data", [])

    def get_comments(self, media_id, fields="id,text,username,timestamp"):
        endpoint = f"{media_id}/comments"
        params = {"fields": fields}
        return self._make_request("GET", endpoint, params).get("data", [])

    def reply_to_comment(self, comment_id, message: str):
        endpoint = f"{comment_id}/replies"
        params = {"message": message}
        return self._make_request("POST", endpoint, params)

    def hide_comment(self, comment_id):
        endpoint = f"{comment_id}"
        params = {"is_hidden": True}
        return self._make_request("POST", endpoint, params)

    def delete_comment(self, comment_id):
        endpoint = f"{comment_id}"
        response = requests.delete(f"{BASE_URL}/{endpoint}", params={"access_token": self.token})
        if response.status_code != 200:
            print(f"\n ERROR AL ELIMINAR: {response.json()}")
        return response.json()