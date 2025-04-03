import requests

class MyAnimeListAPI:
    base_url = "https://api.myanimelist.net/v2/anime/"
    ranking_url = "https://api.myanimelist.net/v2/anime/ranking"

    # Contructor para inicializar el cliente_id
    def __init__(self, client_id):
        self.client_id = client_id
    
    # Metodo para obtener la lista de animes con el ranking por popularidad
    def get_popular_anime(self):
        return self.get_anime_ranking("bypopularity")

    # Metodo para obtener la lista de animes con el ranking por actualmente en emision
    def get_airing_anime(self):
        return self.get_anime_ranking("airing")

    # Metodo para obtener la lista de animes con el ranking por animes que van a salir en emision
    def get_upcoming_anime(self):
        return self.get_anime_ranking("upcoming")

    def get_anime_byId(self, anime_id):
            url = f"{self.BASE_URL}{anime_id}?fields=id,title,main_picture,start_date,end_date,synopsis,mean,rank,popularity,media_type,status,num_episodes,start_season,genres"
            headers = {"X-MAL-CLIENT-ID": self.client_id}
            response = requests.get(url, headers=headers)
            return response.json()
        
    # Metodo par adevolver los animes con el ranking pasado como parametro
    def get_anime_ranking(self, ranking_type):
        url = f"{self.RANKING_URL}?ranking_type={ranking_type}"
        headers = {"X-MAL-CLIENT-ID": self.client_id}
        response = requests.get(url, headers=headers)
        return response.json()
