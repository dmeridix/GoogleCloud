import requests
import webbrowser
import time
import threading
from urllib.parse import urlencode
import yaml
import os
import logging
import json
from flask import Flask, request

# Desactivar logs de Flask (werkzeug)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class MainProgram:
    TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
    API_URL = "https://graphql.anilist.co"
    yaml_file = r"Data/architecture/arq_apicredentials_config.yml"

    # Constructor para inicializar las propiedades de la clase
    def __init__(self):
        self.token_tmp = None
        self.refresh_token_tmp = None
        self.token_expiry_tmp = 0
        self.auth_code = None
        self.shutdown_event = threading.Event()

    # Método principal para obtener el token para las consultas
    def getSources(self, api_name):
        try:
            with open(self.yaml_file, "r") as file:
                data = yaml.safe_load(file)
                print("Datos cargados del archivo YAML:", data) #depuracio
                
            apis = data.get("apis", [])

            for api in apis:
                print("API encontrada:", api) #depuracio
                if api_name in api:
                    print(f"API {api_name} encontrada en la configuración.") #depuracio
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
            print(f"Abre esta URL en tu navegador: {auth_url}")  # Mostrar URL en la terminal si no se abre automáticamente
            webbrowser.open(auth_url)
            print("Autoriza la aplicación en el navegador.")
            return None

    # Inicia un servidor Flask para recibir el código de autorización después de la autenticación
    def start_flask_server(self, auth_config):
        app = Flask(__name__)

        @app.route("/")
        def callback():
            print("[DEBUG] Recibiendo código de autorización...")  # Mensaje de depuración
            code = request.args.get("code")
            if code:
                print(f"[DEBUG] Código de autorización recibido: {code}")
                self._exchange_auth_code_for_token(code, auth_config)
                self.shutdown_event.set()  # Detiene el servidor Flask después de recibir el código
                return """
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
                print("[ERROR] No se recibió un código de autorización.")
                return "Error: No se recibió un código."

        # Asegura que Flask se ejecute en un hilo diferente
        def run_flask():
            try:
                print("[DEBUG] Iniciando servidor Flask en el puerto 8080...")  # Mensaje para asegurarse de que Flask se inicie
                app.run(debug=False, host="0.0.0.0", port=8080, use_reloader=False)
            except Exception as e:
                print(f"[ERROR] Error al iniciar el servidor Flask: {e}")

        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True  # El hilo de Flask se cerrará automáticamente cuando el programa termine
        flask_thread.start()

        # Esperamos que el servidor reciba el código de autorización
        print("[DEBUG] Esperando a que Flask reciba el código de autorización...")
        timeout = 300  # Tiempo máximo de espera en segundos (5 minutos)
        elapsed_time = 0
        while not self.shutdown_event.is_set() and elapsed_time < timeout:
            time.sleep(1)  # Espera activa para evitar que el servidor se cierre prematuramente
            elapsed_time += 1
            if self.shutdown_event.is_set():
                print("[DEBUG] Código de autorización procesado correctamente.")
                break

        if not self.shutdown_event.is_set():
            print("[ERROR] Tiempo de espera agotado. No se recibió el código de autorización.")
        print("[DEBUG] Servidor Flask ha terminado correctamente.")

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


#----------------------------------------------------------------------

    # Lee el archivo .yml que el cliente introduce para obtener el nombre de la api que quiere consultar
    def getApiName(self):
        with open(self.yaml_file, "r") as file:
            data = yaml.safe_load(file)
        api_name = data.get("origin")
        if not api_name:
            raise ValueError("No se encontró el campo 'origin' en el archivo .yml")
        return api_name

    # Recibe el nombre de la api y luego lee el archivo arq_api_source_config para coger la info de la api que se va a consultar
    def getApiConfig(self, api_name):
        with open("Data/architecture/arq_api_sources_config.yml", "r") as file:
            config = yaml.safe_load(file)
        for api in config.get("apis", []):
            if api_name in api:
                return api[api_name]
        raise ValueError(f"No se encontró la configuración para la API: {api_name}")
 

    # Llama a la API correspondiente según el nombre de la API
    def callApi(self, api_name, params):
        info_api = self.getApiConfig(api_name)
        
        if api_name == "nasa":
            response = self.buildNasaConsult(info_api, params, api_name)
        elif api_name == "myanimelist":
            response = self.buildMyAnimeConsult(info_api, params, api_name)
        else:
            response = self.buildAniListConsult(info_api.get("base_url"), params, api_name)
        return response.json()

    # Métodos para construir consultas específicas (placeholder)-------------
    
    def buildNasaConsult(self, info_api, params, api_name):
        base_url = info_api.get("base_url")
        endpoint_name = params.get("endpoint")
        api_format = info_api.get("api_format")
        
        try:
            raw_endpoint = info_api["endpoints"][endpoint_name]
        except KeyError as e:
            raise ValueError(f"El endpoint '{endpoint_name}' no está definido en la config de la API '{api_name}'")
        
        # Formatea el endpoint con los parámetros que se hayan proporcionado
        try:
            endpoint = raw_endpoint.format(**params)
        except KeyError as e:
            raise ValueError(f"Falta el parámetro requerido en 'params' para formatear el endpoint: {e}")
        
        
        token = self.getSources(api_name)
        if not token:
             raise ValueError(f"No se pudo obtener el token para la API '{api_name}'")
        
        # Construye la URL final, añadiendo el token como un parámetro en la URL
        url = f"{base_url}{endpoint}&{api_format}={token}" 
        
        response = requests.get(url)
        return response
        

    def buildMyAnimeConsult(self, info_api, params, api_name):
        
        print(f"api_name: {api_name}")
        print(f"params: {params}") 
        
        base_url = info_api.get("base_url")
        endpoint_name = params.get("endpoint")
        
        print("endpoint_name:", endpoint_name)
        print("endpoints disponibles:", info_api["endpoints"].keys())
        
        # Intenta formatear el endpoint con los parámetros dentro de 'param'
        try:
            endpoint = info_api["endpoints"][endpoint_name].format(**params["param"])
        except KeyError as e:
            #raise ValueError(f"Falta el parámetro requerido en 'params': {e}")
            raise ValueError(f"El endpoint '{endpoint_name}' no existe en la configuración.")
        
        # Obtiene el formato de autenticación (api_format) y el token de autenticación
        api_format = info_api.get("api_format")
        token = self.getSources(api_name)
        
        url = base_url + endpoint
        
        # Configura los encabezados para la solicitud, agregando el token con el formato correspondiente
        headers = {
            api_format: token
        } 
        
        response = requests.get(url, headers=headers)
        return response


    def buildAniListConsult(self, base_url, body, api_name):
        token = self.getSources(api_name)
        page = 1
        perPage = 10
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        endpoint = body.get("endpoint")
        query_params = body.get("query_params", {})
        
        if endpoint == "search_by_id":
            graphql_query = {
                "query": """
                    query ($id: Int) {
                        Media(id: $id, type: ANIME) {
                            id
                            title {
                                romaji
                                english
                                native
                            }
                            coverImage {
                                large
                            }
                        }
                    }
                """,
                "variables": {"id": query_params.get("id")},
            }
        elif endpoint == "search_by_name":
            graphql_query = {
                "query": """
                    query ($name: String, $page: Int, $perPage: Int) {
                        Page(page: $page, perPage: $perPage) {
                            media(search: $name, type: ANIME) {
                                id
                                title {
                                    romaji
                                    english
                                    native
                                }
                                coverImage {
                                    large
                                }
                            }
                        }
                    }
            """,
            "variables": {
                "name": query_params.get("name"),
                "page": page,
                "perPage": perPage
            },
        }
        elif endpoint == "search_by_genre":
            graphql_query = {
                "query": """
                    query ($genre: String, $page: Int, $perPage: Int) {
                        Page(page: $page, perPage: $perPage) {
                            media(genre: $genre, type: ANIME) {
                                id
                                title {
                                    romaji
                                    english
                                    native
                                }
                                coverImage {
                                    large
                                }
                            }
                        }
                    }
                """,
                "variables": {
                    "genre": query_params.get("genre"),
                    "page": page,
                    "perPage": perPage
                },
            }
        else:
            raise ValueError(f"Consulta no identificada: {endpoint}")
        
        response = requests.post(base_url, json=graphql_query, headers=headers)
        return response


if __name__ == "__main__":
    #print("Directorio actual de trabajo:", os.getcwd())
    
    try:
        user_yaml_file = input("Introduce el nombre de tu archivo .yml: ")
        if not user_yaml_file.endswith((".yml", ".yaml")):
            raise ValueError("El archivo debe tener una extensión .yml o .yaml")
        
        # Si el archivo está en el directorio actual, usamos la ruta relativa
        if not os.path.isabs(user_yaml_file):
            user_yaml_file = os.path.join(os.getcwd(), user_yaml_file)
        
        # Verificar si el archivo existe
        if not os.path.exists(user_yaml_file):
            raise FileNotFoundError(f"El archivo {user_yaml_file} no se encuentra en el directorio actual.")
        
        program = MainProgram()
        
        with open(user_yaml_file, "r") as file:
            data = yaml.safe_load(file)
        
        # Obtener el nombre de la API
        api_name = data.get("origin")
        if not api_name:
            raise ValueError("No se encontró el campo 'origin' en el archivo .yml")
        
        # Obtener el cuerpo de la consulta
        body = data.get("jobs", [{}])[0]

        # Intentar obtener el token directamente
        token_obtenido = program.getSources(api_name)

        # Si no se encuentra el token, iniciar la autorización
        if not token_obtenido:
            try:
                with open(program.yaml_file, "r") as file:
                    config_data = yaml.safe_load(file)
                apis = config_data.get("apis", [])
                auth_config = None
                for api in apis:
                    if api_name in api:
                        auth_config = api[api_name]["auth"]
                        break
                if not auth_config:
                    raise ValueError(f"No se encontró la configuración de autenticación para '{api_name}'.")
            except Exception as e:
                print(f"Error al leer el archivo de configuración de autenticación: {e}")
                exit(1)

            # Iniciar el servidor Flask para obtener el código de autorización
            program.start_flask_server(auth_config)

            # Intentar obtener el token nuevamente después de la autorización
            token_obtenido = program.getSources(api_name)
            if not token_obtenido:
                raise ValueError(f"No se pudo obtener el token después de la autorización para '{api_name}'.")

        # Llamar a la API correspondiente
        result = program.callApi(api_name, body)

        # Guardar el resultado en un archivo JSON
        output_folder = "output_results"
        os.makedirs(output_folder, exist_ok=True)
        
        output_file = os.path.join(output_folder, f"{api_name}_result.json")
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)
        
        print(f"Resultado guardado en: {output_file}")
    
    except Exception as e:
        print(f"Error main: {e}")