import requests
import sys
import json

""" Class to perform all Spotify related operations using Web API """
class Spotify:

    __api_url = 'https://api.spotify.com/v1/'

    def __init__(self):
        pass

    def search(self, query_string, search_limit=1):
        url = self.__api_url + 'search?type=track&limit=' + str(search_limit) + '&q=' + query_string

        r = requests.get(url)
        if r.status_code != 200:
            print('search request failed:',r.status_code,file=sys.stderr)
            return None
        response_json = json.loads(r.text)

        search_results = []
        for i in range(search_limit):
            artist = response_json['tracks']['items'][i]['artists'][0]['name']
            title = response_json['tracks']['items'][i]['name']
            album = response_json['tracks']['items'][i]['album']['name']
            id = response_json['tracks']['items'][i]['id']
            uri = response_json['tracks']['items'][i]['uri']
            spotify_url = response_json['tracks']['items'][i]['external_urls']['spotify']
            result = {
                'artist':artist,
                'title':title,
                'album':album,
                'id':id,
                'spotify_url':spotify_url,
                'uri':uri
            }
            search_results.append(result)

        if search_limit == 1:
            return search_results[0]
        else:
            return search_results
