import requests

class NASA_API:
    BASE_URL = "https://api.nasa.gov"
    API_KEY = "13kRF4pk6oMPewjkKx4R7i4h9el95QMzAMGGHyww"

    # Metodo para obtener la 'Astronomy Picture of the Day' (APOD) e información de la NASA .
    def get_apod(self):
        url = f"{self.BASE_URL}/planetary/apod?api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()

    # Metodo para obtener un feed diario de asteroides cercanos a la Tierra
    def get_asteroid_info(self):
        url = f"{self.BASE_URL}/neo/rest/v1/feed?api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()

    # Metodo para obtener una lista de patentes relacionadas con la transferencia de tecnología de la NASA.
    def get_exploration_reports(self):
        # Nuevo endpoint para patentes de transferencia de tecnología
        url = f"{self.BASE_URL}/techtransfer/patent/?engine&api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()

    # Método para obtener una imagen satelital de la Tierra en coordenadas específicas.
    def get_earth_image(self, lat, lon, dim=0.1):
        url = f"{self.BASE_URL}/planetary/earth/imagery?lon={lon}&lat={lat}&dim={dim}&api_key={self.API_KEY}"
        response = requests.get(url)
        return response.json()