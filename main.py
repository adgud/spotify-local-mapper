import os
import sys
from mutagen.id3 import ID3, ID3NoHeaderError
from spotify import Spotify


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


def main():
    music_dir = input('Directory with MP3 files: ')
    mp3_files = get_mp3_files(music_dir)

    playlist_name = input('Playlist name to be created: ')
    spotify_username = input('Spotify username: ')
    sp = Spotify()
    sp.auth(spotify_username)
    playlist_id = sp.create_playlist(playlist_name)

    for file in mp3_files:
        print('\nProcessing ', file, '...')
        tags = read_id3(file)
        if tags is None:
            continue

        search_result = sp.search(tags['artist'] + ' ' + tags['title'])
        if search_result is None:
            continue

        sp.add_tracks_to_playlist(playlist_id, search_result['uri'])


if __name__ == '__main__':
    main()
