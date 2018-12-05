import pandas as pd
import numpy as np
import sklearn.metrics as skmet
import re
import os


def main(feature, high_low):
   # Pulling and formatting artists songs
   path = "{}/data/artist_track_features.csv".format(os.path.dirname(os.path.realpath(__file__)))
   artist_songs = pd.read_csv(path, low_memory=False, encoding="ISO-8859-1")
   artist = 'diiv'  # this should be made dynamic for the final
   artist_songs['artist'] = artist
   # artist_songs.head()

   # Pulling and formatting pool of playlist songs
   path = "{}/data/related_artist_track_features.csv".format(os.path.dirname(os.path.realpath(__file__)))
   song_pool = pd.read_csv(path, low_memory=False, encoding="ISO-8859-1".format(path))
   #song_pool = song_pool.drop('Artists', 1)
   song_pool = song_pool.set_index('track_id')
   # song_pool.head()

   # User inputs
   feature = feature  # input("Enter a music quality you're looking for: ").lower()
   intensity = high_low  # input("Are you looking for songs with max or min of this feature?").lower()
   # artist_song_vector = artist_songs[artist_songs["{}".format(feature)] > .8]

   # Filtered list length to be roughly the top 10% of artists tracks with the desired feature.
   if len(artist_songs) <= 10:
      n = 1
   else:
      n = int(len(artist_songs)*.1)

   # Filtering the list and returning a ideal artist_song vector.
   if intensity == 'high':
      artist_song_vector = artist_songs.nlargest(n, "{}".format(feature), keep='first').groupby(artist_songs['artist']).mean()
   elif intensity == 'low':
      artist_song_vector = artist_songs.nsmallest(n, "{}".format(feature), keep='first').groupby(artist_songs['artist']).mean()
   else:
      intensity = input("Please enter either max or min for how much of this quality you're looking for in your playlist").lower()

   # finding the similarity of songs in song pool to artist_song vector
   cos_sim = skmet.pairwise.cosine_similarity(artist_song_vector, song_pool, dense_output=True)
   a = cos_sim.tolist()[0]
   
   # filtering song pool to 25 most similar songs
   song_pool['cos_sim'] = a
   playlist = song_pool.nlargest(25, "cos_sim", keep='first').reset_index()
   
   # Saving playlist to CSV
   playlist_name = intensity + "_" + feature + "_" + artist
   # dir_path = os.path.dirname(os.path.realpath(__file__)) # when building with a IDE use this.
   # csv_file = "{}/data/{}.csv".format(dir_path, playlistname) # when building with a IDE use this.
   path = "{}/data/analysis.csv".format(os.path.dirname(os.path.realpath(__file__)))
   playlist.to_csv(path, index=False)

main('loudness', 'low')
