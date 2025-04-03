import requests
import webbrowser
import time
from urllib.parse import urlencode
import yaml
from flask import Flask, request
import sys  # Para salir del programa después de la autorización

app = Flask(__name__)

class MainProgram:
    TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
    API_URL = "https://graphql.anilist.co"
    yaml_file = r"C:\Users\DANIELMERIDACORDERO\GoogleCloud\Data\architecture\arq_apicredentials_config.yml"

    def __init__(self):
        self.token_tmp = None
        self.refresh_token_tmp = None
        self.token_expiry_tmp = 0
        self.auth_code = None  # Para almacenar el código de autorización

    # Método que lee el yml y devuelve los tokens correspondientes de cada API
    def getSources(self, api_name):
        with open(self.yaml_file, "r") as file:
            data = yaml.safe_load(file)
        apis = data.get("apis", [])

        for api in apis:
            if api_name in api:
                if api_name == "anilist":
                    auth_config = api[api_name]["auth"]
                    return self.get_token(auth_config)
                else:
                    return api[api_name]["auth"].get("access_token")
        return None

    # Lógica para obtener el token para cada API
    def get_token(self, auth_config):
        current_time = time.time()

        # Si el token sigue vigente, lo usamos
        if self.token_tmp and current_time < self.token_expiry_tmp:
            return self.token_tmp

        # Si el token ha expirado, intentamos refrescarlo con el refresh token
        if self.refresh_token_tmp:
            return self._refresh_or_request_token(auth_config)

        # Si no hay token o refresh token, solicitamos uno nuevo
        return self._refresh_or_request_token(auth_config)

    # Método para refrescar o solicitar un nuevo token para cada API
    def _refresh_or_request_token(self, auth_config):
        if self.refresh_token_tmp:
            # Refrescar el token de la API correspondiente
            data = {
                "grant_type": "refresh_token",
                "client_id": auth_config["client_id"],
                "client_secret": auth_config["client_secret"],
                "refresh_token": self.refresh_token_tmp,
            }
            response = requests.post(self.TOKEN_URL, data=data)
            token_data = response.json()
            self.token_tmp = token_data.get("access_token")
            self.refresh_token_tmp = token_data.get("refresh_token")
            self.token_expiry_tmp = time.time() + 3600  # El token expira en una hora
        else:
            # Solicitar un nuevo token de la API correspondiente
            params = {
                "client_id": auth_config["client_id"],
                "redirect_uri": auth_config["redirect_uri"],
                "response_type": "code",
            }
            auth_url = f"https://anilist.co/api/v2/oauth/authorize?{urlencode(params)}"
            webbrowser.open(auth_url)
            print("Por favor, autoriza la aplicación en el navegador. El programa continuará después de la autorización.")
            return None  # El flujo se interrumpirá aquí hasta que se reciba el código de autorización

    # Método para manejar el código de autorización en la URL
    @app.route("/callback")
    def callback():
        code = request.args.get("code")
        if code:
            program.auth_code = code
            print("Código de autorización recibido.")
            program._exchange_auth_code_for_token(code)  # Intercambia el código por el token
            return "Autorización completada. Puedes cerrar esta ventana."

    # Método para intercambiar el código de autorización por el token
    def _exchange_auth_code_for_token(self, code):
        data = {
            "grant_type": "authorization_code",
            "client_id": "25596",  # Tu client_id
            "client_secret": "iG1vmez3bj55ozAe8EaR8Y5LjqtHAU0iVAg9UjkM",  # Tu client_secret
            "redirect_uri": "http://localhost:8080",
            "code": code,
        }

        response = requests.post(self.TOKEN_URL, data=data)
        token_data = response.json()
        self.token_tmp = token_data.get("access_token")
        self.refresh_token_tmp = token_data.get("refresh_token")
        self.token_expiry_tmp = time.time() + 3600  # El token expira en una hora
        print(f"Token obtenido: {self.token_tmp}")

# Usar el código con el YAML
if __name__ == "__main__":
    program = MainProgram()
    auth_config = program.getSources("anilist")
    if auth_config is None:
        app.run(debug=True, port=8080)  # Iniciar Flask solo si el código de autorización está pendiente
