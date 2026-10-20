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
        print(f" InstagramService inicializado con cuenta ID: {self.business_id}")

    def get_media(self, fields="id,caption,comments_count", limit=25):
        url = f"{BASE_URL}/{self.business_id}/media"
        params = {"access_token": self.token, "fields": fields, "limit": limit}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_comments(self, media_id, fields="id,text,username,timestamp"):
        url = f"{BASE_URL}/{media_id}/comments"
        params = {"access_token": self.token, "fields": fields}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def reply_to_comment(self, comment_id, message: str):
        url = f"{BASE_URL}/{comment_id}/replies"
        params = {"access_token": self.token, "message": message}
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def hide_comment(self, comment_id):
        url = f"{BASE_URL}/{comment_id}"
        params = {"access_token": self.token, "is_hidden": True}
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        return resp.json()