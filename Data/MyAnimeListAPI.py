import requests
from urllib.parse import urlencode

class AniListAuth:
    auth_url = "https://anilist.co/api/v2/oauth/authorize"
    token_tmp = "https://anilist.co/api/v2/oauth/token"
    api_url = "https://graphql.anilist.co"

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
        return f"{self.auth_url}?{urlencode(params)}"

    def get_access_token(self, auth_code):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": auth_code,
        }
        response = requests.post(self.token_tmp, data=data)
        token_data = response.json()
        self.access_token = token_data.get("access_token")
        return self.access_token

    def get_user_data(self):
        if not self.access_token:
            raise ValueError("Access token is required.")
        query = """
        query {
            Viewer {
                id
                name
            }
        }
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(self.api_url, json={"query": query}, headers=headers)
        return response.json()