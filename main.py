import os
import requests
import json
from spotify import Spotify


def get_mp3_files(path):
    mp3_files = []
    for path, dirs, files in os.walk(path):
        for name in files:
            if name.endswith('.mp3'):
                mp3_files.append(os.path.join(path, name))
    return mp3_files

def get_mp3_tags(filename):
    from mutagen.id3 import ID3
    audio = ID3(filename)
    title = audio["TIT2"].text[0]
    artist = audio['TPE1'].text[0]
    album = audio['TALB'].text[0]
    return {'artist':artist, 'title':title, 'album':album}


def main():
    # testing area below

    music_path = './test_media'
    files = get_mp3_files(music_path)
    f = files[0]
    print(f)
    tags = get_mp3_tags(f)
    print(tags)

    q = 'Gianna+Nannini+Meravigliosa+Creatura'
    spotify = Spotify()

    print(spotify.search(q))


if __name__ == '__main__':
    main()
