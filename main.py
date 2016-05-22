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
    # testing area below

    music_path = './test_media'
    files = get_mp3_files(music_path, include_subdirs=True)
    print(files)
    f = files[len(files)-1]
    print(f)
    tags = read_id3(f)
    print(tags)

    q = 'Gianna Nannini Meravigliosa Creatura'
    spotify = Spotify()

    print(spotify.search(q))


if __name__ == '__main__':
    main()
