import requests
import sys
import json
import random
import urllib.parse
import webbrowser
import time


class Spotify:
    """ Class to perform all Spotify related operations using Web API """
    __API_URL = 'https://api.spotify.com/v1/'
    __AUTH_URL = 'https://accounts.spotify.com/authorize'
    __access_token = None

    def __init__(self):
        pass

    def search(self, query_string, search_limit=1):
        params = {
            'type': 'track',
            'limit': str(search_limit),
            'q': query_string
        }
        url = self.__API_URL + 'search'
        search_request = requests.get(url, params=params)

        if search_request.status_code != 200:
            print('search request failed:', search_request.status_code, file=sys.stderr)
            return None
        response_json = search_request.json()

        if response_json['tracks']['total'] == 0:
            print('nothing found:',query_string, file=sys.stderr)
            return None

        search_results = []
        for i in range(search_limit):
            artist = response_json['tracks']['items'][i]['artists'][0]['name']
            title = response_json['tracks']['items'][i]['name']
            album = response_json['tracks']['items'][i]['album']['name']
            track_id = response_json['tracks']['items'][i]['id']
            uri = response_json['tracks']['items'][i]['uri']
            spotify_url = response_json['tracks']['items'][i]['external_urls']['spotify']
            result = {
                'artist': artist,
                'title': title,
                'album': album,
                'id': track_id,
                'spotify_url': spotify_url,
                'uri': uri
            }
            search_results.append(result)

        if search_limit == 1:
            return search_results[0]
        else:
            return search_results

    def auth(self, client_id, redirect_uri, dialog=False):
        # use implicit grant
        response_type = 'token'
        scope = 'playlist-read-private playlist-modify-private'
        state = str(random.getrandbits(256))
        show_dialog = 'true' if dialog else 'false'
        params = {
            'client_id': client_id,
            'response_type': response_type,
            'redirect_uri': redirect_uri,
            'state': state,
            'scope': scope,
            'show_dialog': show_dialog
        }
        auth_url = self.__AUTH_URL + '?' + urllib.parse.urlencode(params)
        print('waiting for authorization...')
        webbrowser.open(auth_url)
        auth_check_url = redirect_uri + '?state=' + state
        # start polling
        i = 0
        while i < 10:
            time.sleep(3)
            auth_check_request = requests.get(auth_check_url)

            if auth_check_request.status_code == 200:
                self.__access_token = auth_check_request.text
                return

            i += 1

        print('timeout when waiting for access token')

    def get_access_token(self):
        return self.__access_token

    def create_playlist(self, username, playlist_name, public=False):
        if self.__access_token is None:
            print('not authorized yet', file=sys.stderr)
            raise ValueError

        headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json'
        }
        data = {
            'name': playlist_name,
            'public': 'true' if public else 'false'
        }
        payload = json.dumps(data)
        url = self.__API_URL + 'users/' + username + '/playlists'
        create_playlist_request = requests.post(url, data=payload, headers=headers)
        response = create_playlist_request.json()
        if create_playlist_request.status_code == 201:
            return response['id']
        else:
            print(response, file=sys.stderr)
            return None

    def add_tracks_to_playlist(self, username, playlist_id, track_ids, position=None):
        if self.__access_token is None:
            print('not authorized yet', file=sys.stderr)
            raise ValueError

        headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json'
        }

        uris = ''
        if type(track_ids) is list:
            for track_id in track_ids:
                uris += track_id + ','
            uris = uris[:-1]    # strip last comma
        else:
            uris = track_ids

        params = {
            'position': position,
            'uris': uris
        }

        url = self.__API_URL + 'users/' + username + '/playlists/' + playlist_id + '/tracks'
        add_tracks_request = requests.post(url, params=params, headers=headers)
        response = add_tracks_request.json()
        if add_tracks_request.status_code == 201:
            return response['snapshot_id']
        else:
            print(response, file=sys.stderr)
            return None
