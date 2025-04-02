clase MyAnimeListAPI:
    base_url = "https://api.myanimelist.net/v2/anime/"
    def __init__(self, client_id):
        self.client_id = client_id
    
    def