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