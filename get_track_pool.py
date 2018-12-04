import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import csv
import os
import math


data_path = "{}/data".format(os.path.dirname(os.path.realpath(__file__)))

if not os.path.exists(data_path):
    os.makedirs(data_path)

# spotify API creds
client_id = 'f679c1432cb2400d91774735c9a70fe9'
client_secret = '89893542a76748a8aa60fc35fb93c29b'

# init spotipy client
client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_artist_info(artist):
    response = sp.search(q=artist, limit=1, type='artist')
    return (response['artists']['items'][0]['id'], response['artists']['items'][0]['uri'])


def get_related_artist_ids(artist_uri):
    related = sp.artist_related_artists(artist_uri)
    related_artists = []

    for artist in related['artists']:
        related_artists.append((artist['name'], artist['id']))
    return related_artists


def get_artist_tracks(artist_id):
    albums = []
    artist_tracks = []
    results = sp.artist_albums(artist_id, album_type='album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    unique = set()  # skip duplicate albums
    for album in albums:
        name = album['name'].lower()
        if name not in unique:
            unique.add(name)
            artist_tracks.extend(get_album_tracks(album))
    return artist_tracks


def get_album_tracks(album):
    tracks = []
    track_ids = []
    tracks_with_names = []

    results = sp.album_tracks(album['id'])
    tracks.extend(results['items'])

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for track in tracks:
        track_ids.append(track['id'])

    return track_ids


def get_track_features(track_ids):
    response = []
    tracks_with_features = []

    if len(track_ids) > 100:
        # get current length
        length = len(track_ids)

        batches = math.ceil(length / 100)

        for i in range(batches):
            batch = track_ids[100*i:99+(100*i)]
            batch_response = sp.audio_features(batch)
            response.extend(batch_response)
    else:
        response = sp.audio_features(track_ids)

    for track in response:
        row = {
            "track_id": track['id'],
            "danceability": track['danceability'],
            "energy": track['energy'],
            "key": track['key'],
            "loudness": track['loudness'],
            "mode": track['mode'],
            "speechiness": track['speechiness'],
            "acousticness": track['acousticness'],
            "instrumentalness": track['instrumentalness'],
            "liveness": track['liveness'],
            "valence": track['valence'],
            "tempo": track['tempo']
        }
        tracks_with_features.append(row)

    return tracks_with_features


def write_to_csv(tracks_with_features, related):
    columns = [
        'track_id',
        'danceability',
        'energy',
        'key',
        'loudness',
        'mode',
        'speechiness',
        'acousticness',
        'instrumentalness',
        'liveness',
        'valence',
        'tempo'
    ]

    if related:
        csv_file = "{}/related_artist_track_features.csv".format(data_path)
    else:
        csv_file = "{}/artist_track_features.csv".format(data_path)

    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for row in tracks_with_features:
                writer.writerow(row)
    except IOError:
        print("I/O error")
