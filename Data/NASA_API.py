import requests
import webbrowser
from urllib.parse import urlencode
class NASA_API:
    BASE_URL = "https://api.nasa.gov"
    API_KEY = "13kRF4pk6oMPewjkKx4R7i4h9el95QMzAMGGHyww"

    def get_apod(self):
        url = f"{self.BASE_URL}/planetary/apod?api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()

    def get_asteroid_info(self):
        url = f"{self.BASE_URL}/neo/rest/v1/feed?api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()

    def get_exploration_reports(self):
        url = f"{self.BASE_URL}/techport/api/projects?api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()

    def get_earth_image(self, lat, lon, dim=0.1):
        url = f"{self.BASE_URL}/planetary/earth/imagery?lon={lon}&lat={lat}&dim={dim}&api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()