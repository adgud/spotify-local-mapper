import os
import sys
import urllib
import webbrowser

import spotipy
from mutagen.id3 import ID3, ID3NoHeaderError


def get_mp3_files(path, include_subdirs=True):
    mp3_files = []

    if include_subdirs:
        for path, dirs, files in os.walk(path):
            for name in files:
                if name.endswith('.mp3'):
                    mp3_files.append(os.path.join(path, name))
    else:
        all_files = os.listdir(path)
        for name in all_files:
            if name.endswith('.mp3'):
                mp3_files.append(os.path.join(path, name))

    return mp3_files


def read_id3(filename):
    try:
        audio = ID3(filename)
    except (ID3NoHeaderError, FileNotFoundError) as e:
        print('failed to read ID3 data from', filename, ':', str(e), file=sys.stderr)
        return None

    title, artist, album = '', '', ''
    # todo: properly convert to utf8
    try:
        title = audio["TIT2"].text[0]
    except KeyError as e:
        print('failed to read ID3 tag', str(e), 'from:', filename, file=sys.stderr)

    try:
        artist = audio['TPE1'].text[0]
    except KeyError as e:
        print('failed to read ID3 tag', str(e), 'from:', filename, file=sys.stderr)

    try:
        album = audio['TALB'].text[0]
    except KeyError as e:
        print('failed to read ID3 tag', str(e), 'from:', filename, file=sys.stderr)

    if title == '' and artist == '' and album == '':
        print('no tags found for file', filename, file=sys.stderr)
        return None

    return {'artist':artist, 'title':title, 'album': album}


def get_spotify_auth_token(client_id, redirect_url, dialog=False):
    params = {
        'client_id': client_id,
        'response_type': 'token',
        'redirect_uri': redirect_url,
        'scope': 'playlist-read-private playlist-modify-private playlist-modify-public playlist-read-collaborative',
        'show_dialog': 'true' if dialog else 'false'
    }
    auth_url = 'https://accounts.spotify.com/authorize' + '?' + urllib.parse.urlencode(params)
    webbrowser.open(auth_url)
    return input('Paste token here: ')


def main():
    music_dir = input('Directory with MP3 files: ')
    mp3_files = get_mp3_files(music_dir)

    playlist_name = input('Playlist name to be created: ')
    spotify_username = input('Spotify username: ')

    client_id = '6224d6d8e66045b59ce328d043aa4b5d'
    redirect_url = 'https://adgud.github.io/spotify-local-mapper/callback/'
    token = get_spotify_auth_token(client_id, redirect_url)
    sp = spotipy.Spotify(auth=token)
    playlist = sp.user_playlist_create(spotify_username, 'test', public=False)
    playlist_id = playlist['id']

    for file in mp3_files:
        print('\nProcessing ', file, '...')
        tags = read_id3(file)
        if tags is None:
            continue

        query = tags['artist'] + ' ' + tags['title']
        search_result = sp.search(query)
        if len(search_result['tracks']['items']) == 0:
            print('Nothing found for "', query, '"', file=sys.stderr)
            continue

        track_uri = search_result['tracks']['items'][0]['uri']
        sp.user_playlist_add_tracks(spotify_username, playlist_id, [track_uri])
        print('Added "', search_result['tracks']['items'][0]['name'], '" by ', search_result['tracks']['items'][0]['artists'][0]['name'])


if __name__ == '__main__':
    main()
