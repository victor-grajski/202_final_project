import spotipy
import spotipy.util as util
import pprint
import subprocess
import os
import csv


# spotify API creds
client_id = 'f679c1432cb2400d91774735c9a70fe9'
client_secret = '89893542a76748a8aa60fc35fb93c29b'
redirect_uri = 'http://localhost/callback/'
scope = 'playlist-modify-public'
username = '1211837635'

token = util.prompt_for_user_token(
    username=username,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri
)

sp = spotipy.Spotify(auth=token)
sp.trace = False


def create_playlist(playlist_name):
    playlist = sp.user_playlist_create(username, playlist_name)
    return (playlist['id'], playlist['external_urls']['spotify'])


def read_csv(analysis_path):
    track_ids = []

    with open(analysis_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                track_ids.append(row[0])
    return track_ids
