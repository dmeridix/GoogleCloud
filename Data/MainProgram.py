import requests

import requests
import webbrowser
import time
import threading
from urllib.parse import urlencode
import yaml
import os
import logging
from flask import Flask, request

# Desactivar logs de Flask (werkzeug)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class MainProgram:
    TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
    API_URL = "https://graphql.anilist.co"
    yaml_file = r"C:\Users\DANIELMERIDACORDERO\GoogleCloud\Data\architecture\arq_apicredentials_config.yml"

    # Constructor para inicializar las propiedades de la clase
    def __init__(self):
        self.token_tmp = None
        self.refresh_token_tmp = None
        self.token_expiry_tmp = 0
        self.auth_code = None
        self.shutdown_event = threading.Event()

    # Método principal para obtener el token temporal
    def getSources(self, api_name):
        try:
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
        except Exception as e:
            print(f"Error al leer el archivo YAML: {e}")
            return None

    # Verifica si hay un token válido almacenado, si no, obtiene uno nuevo o lo refresca
    def get_token(self, auth_config):
        current_time = time.time()

        if self.token_tmp and current_time < self.token_expiry_tmp:
            return self.token_tmp

        if self.refresh_token_tmp:
            return self._refresh_or_request_token(auth_config)

        return self._refresh_or_request_token(auth_config)

    # Intenta refrescar el token si ya existe, o solicita uno nuevo si no hay un refresh token disponible
    def _refresh_or_request_token(self, auth_config):
        if self.refresh_token_tmp:
            data = {
                "grant_type": "refresh_token",
                "client_id": auth_config["client_id"],
                "client_secret": auth_config["client_secret"],
                "refresh_token": self.refresh_token_tmp,
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.TOKEN_URL, json=data, headers=headers)
            token_data = response.json()
            self.token_tmp = token_data.get("access_token")
            self.refresh_token_tmp = token_data.get("refresh_token")
            self.token_expiry_tmp = time.time() + 3600
        else:
            # Si no hay refresh token, solicita autorización al usuario
            params = {
                "client_id": auth_config["client_id"],
                "redirect_uri": auth_config["redirect_uri"],
                "response_type": "code",
            }
            auth_url = f"https://anilist.co/api/v2/oauth/authorize?{urlencode(params)}"
            webbrowser.open(auth_url)
            print("Autoriza la aplicación en el navegador.")
            return None

    # Inicia un servidor Flask para recibir el código de autorización después de la autenticación
    def start_flask_server(self, auth_config):
        app = Flask(__name__)

        @app.route("/")
        def callback():
            code = request.args.get("code")
            if code:
                print("Código de autorización recibido")
                self._exchange_auth_code_for_token(code, auth_config)
                self.shutdown_event.set()  # Marca el evento para detener Flask

                # HTML con JavaScript para cerrar la pestaña automáticamente
                return """
                <html>
                    <body>
                        <p>Autorización completada. Esta ventana se cerrará automáticamente.</p>
                        <script>
                <html>
                    <body>
                        <p>Autorización completada. Esta ventana se cerrará automáticamente.</p>
                        <script>
                            setTimeout(() => { window.close(); }, 2000);
                        </script>
                    </body>
                </html>
                """
            else:
                return "Error: No se recibió un código."

        # Ejecutar Flask en un hilo separado
        def run_flask():
            app.run(debug=False, port=8080, use_reloader=False)

        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()

        # Esperar hasta que la autorización esté completa
        self.shutdown_event.wait()
        print("Cerrando servidor Flask...")

    # Intercambia el código de autorización por un token de acceso
    def _exchange_auth_code_for_token(self, code, auth_config):
        data = {
            "grant_type": "authorization_code",
            "client_id": auth_config["client_id"],
            "client_secret": auth_config["client_secret"],
            "redirect_uri": auth_config["redirect_uri"],
            "code": code,
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.TOKEN_URL, json=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            self.token_tmp = token_data.get("access_token")
            self.refresh_token_tmp = token_data.get("refresh_token")
            self.token_expiry_tmp = time.time() + 3600
            print("Token temporal obtenido")

        except requests.exceptions.RequestException as e:
            print("Error al obtener el token")

if __name__ == "__main__":
    program = MainProgram()
    auth_config = program.getSources("anilist")

    if auth_config is None:
        try:
            with open(program.yaml_file, "r") as file:
                data = yaml.safe_load(file)
            apis = data.get("apis", [])
            for api in apis:
                if "anilist" in api:
                    auth_config = api["anilist"]["auth"]
                    break
        except Exception as e:
            print(f"Error al leer el archivo YAML: {e}")

        program.start_flask_server(auth_config)

    token_obtenido = program.getSources("anilist")
    print(f"Token final obtenido: {token_obtenido}")