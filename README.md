# spotify-local-mapper

## Description
A simple tool to map you local media files into a playlist on Spotify using Python 3.

## Installation
Make sure that the dependecies are installed, then simply download the script and run it. 

## Spotify authentication
This script will use API keys loaded from file `spotify_api_keys.json` and use [Spotify Authorization Code Flow](https://developer.spotify.com/web-api/authorization-guide/#authorization_code_flow) if such file exists in the script directory. This file should have the following format:
```
{
  "client_id": "SPOTIFY_CLIENT_ID,
  "client_secret": "SPOTIFY_CLIENT_SECRET",
  "callback_uri": "https://example.com/callback/"
}
```
Authorization will be performed only once and cached tokens will be used in subsequent runs.

If file `spotify_api_keys.json` does not exist or contains malformed data, [Implicit Grant Flow](https://developer.spotify.com/web-api/authorization-guide/#implicit-grant-flow) will be used, using this app's keys. Authorization tokens will be cached only for an hour and you will be propmted for access token again.

### Dependencies
* [mutagen](https://github.com/nex3/mutagen)
* [spotipy](https://github.com/plamere/spotipy)

## Todo
* Convert to proper package, so that dependencies can be installed automatically
* Include interactive mode, where user can select which track should be mapped and change search query