import requests
import webbrowser
from urllib.parse import urlencode

class NASA_API:
    base_url = "https://api.nasa.gov/"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_apod(self):
        url = f"{self.base_url}planetary/apod?api_key={self.api_key}"
        response = requests.get(url)
        return response.json()