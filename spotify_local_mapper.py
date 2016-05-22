import os
import pprint
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
        print('Failed to read ID3 data from', filename, ':', str(e), file=sys.stderr)
        return None

    title, artist, album = '', '', ''
    try:
        title = audio["TIT2"].text[0]
    except KeyError as e:
        print('Failed to read ID3 tag', str(e), 'from:', filename, file=sys.stderr)

    try:
        artist = audio['TPE1'].text[0]
    except KeyError as e:
        print('Failed to read ID3 tag', str(e), 'from:', filename, file=sys.stderr)

    try:
        album = audio['TALB'].text[0]
    except KeyError as e:
        print('Failed to read ID3 tag', str(e), 'from:', filename, file=sys.stderr)

    if title == '' and artist == '' and album == '':
        return None

    return {'artist':artist, 'title':title, 'album': album}


def get_spotify_access_token(client_id, redirect_uri, dialog=False):
    params = {
        'client_id': client_id,
        'response_type': 'token',
        'redirect_uri': redirect_uri,
        'scope': 'playlist-read-private playlist-modify-private playlist-modify-public playlist-read-collaborative',
        'show_dialog': 'true' if dialog else 'false'
    }
    auth_url = 'https://accounts.spotify.com/authorize' + '?' + urllib.parse.urlencode(params)
    webbrowser.open(auth_url)
    return input('Paste token here: ')


def main():
    music_dir = input('Directory with MP3 files: ')
    mp3_files = get_mp3_files(music_dir)
    if len(mp3_files) == 0:
        print('No MP3 files found in', music_dir, file=sys.stderr)
        return

    playlist_name = input('Playlist name to be created: ')
    if playlist_name is '':
        playlist_name = 'imported tracks'

    # you can use your own application created at https://developer.spotify.com/my-applications/
    client_id = '6224d6d8e66045b59ce328d043aa4b5d'
    redirect_uri = 'https://adgud.github.io/spotify-local-mapper/callback/'

    # use own implementation of getting auth token, because the spotipy's is buggy
    access_token = get_spotify_access_token(client_id, redirect_uri)
    sp = spotipy.Spotify(auth=access_token)

    try:
        user_profile = sp.me()
    except spotipy.client.SpotifyException:
        print('Not authorized - did you paste a valid token?', file=sys.stderr)
        return

    spotify_user_id = user_profile['id']
    playlist = sp.user_playlist_create(spotify_user_id, playlist_name, public=False)
    playlist_id = playlist['id']

    files_added = 0
    for file in mp3_files:
        print('\nProcessing', file, '...')
        tags = read_id3(file)
        if tags is None:
            print('No tags found for file', file, file=sys.stderr)
            continue

        query = tags['artist'] + ' ' + tags['title']
        search_result = sp.search(query)
        if len(search_result['tracks']['items']) == 0:
            print('Nothing found for "', query, '"', sep='', file=sys.stderr)
            continue

        track_uri = search_result['tracks']['items'][0]['uri']
        sp.user_playlist_add_tracks(spotify_user_id, playlist_id, [track_uri])
        artist = search_result['tracks']['items'][0]['artists'][0]['name']
        title = search_result['tracks']['items'][0]['name']
        print('Added "', title, '" by ', artist, sep='')
        files_added += 1

    print('\nFinished, successfully added', files_added, 'out of', len(mp3_files), 'files.')

if __name__ == '__main__':
    main()
