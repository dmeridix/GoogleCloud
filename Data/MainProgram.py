import requests
import yaml

class MainProgram:
    def __init__(self, yaml_file):
        self.token = None
        self.yaml_file = yaml_file

    def getSources(self, api_name):
        with open(self.yaml_file, "r") as file:
            data = architecture.arc_api_sources_config.yml(file)
        apis = data.get("apis", [])
        for api in apis:
            if api_name in api:
                self.token = api[api_name]["auth"].get("access_token")
                return api[api_name]
        return None
    
    def getApiName(self):
        with open(self.yaml_file, "r") as file:
            data = yaml.safe_load(file)
        api_name = data.get("origin")
        if not api_name:
            raise ValueError("No se encontró el campo 'origin' en el archivo .yml")
        return api_name
    
    #Lee el archivo arq_api_surce_config para coger la info de  la api que se a introducido en el input.yml
    def getApiConfig(self, api_name):
        with open("arq_api_source_config.yml", "r") as file:
            config = yaml.safe_load(file)
        for api in config.get("apis", []):
            if api_name in api_name:
                return api[api_name]
            
        raise ValueError(f"No se encontró la configuración para la API: {api_name}")
    
    def buildApiUrl(self, api_name, endpint_name, params=None):
        api_config = self.getApiConfig(api_name)
        base_url = api_config.get["base_url"]
        #CONTINUAR con lo que queda de codigo apuntado en la libreta 

    def callApi (self):
        api_name = self.getApiName()
        token = self.getSources(api_name)

        with open (self.yaml_file, "r") as file:
            data = yaml.safe_load(file)

            endpoint = data["jobs"][0]
    #acabar este metodo despues de acabar buildApiUrl y verificar los parametros de cada metodo y que coincidan con el .yml



        
    if __name__ == "__main__":
        yaml_file = input("Introduce el nombre de tu archvo .yml: ")
        
        data = getSources(yaml_file)

        if data:
            consulta_api(data)