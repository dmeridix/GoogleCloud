import requests
import webbrowser
from urllib.parse import urlencode

class AniListAuth:
    AUTH_URL = "https://anilist.co/api/v2/oauth/authorize"
    TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
    API_URL = "https://graphql.anilist.co"

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None

    def get_auth_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def get_access_token(self, auth_code):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": auth_code,
        }
        response = requests.post(self.TOKEN_URL, data=data)
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        return self.access_token
