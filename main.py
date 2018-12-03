import sys
import os
import shutil
import get_track_pool
import analyse_track_pool
import create_playlist


def main():
    print("This program takes an artist (ex: Radiohead) and a song feature (ex: Danceability), and it creates a Spotify playlist of the songs that most correspond to that feature in the discographies of the artists related to the one you specify. Enjoy!")

    artist = input("Enter an artist: ")

    print("Available song features:")
    print("Danceability")
    print("Energy")
    print("Loudness")
    print("Speechiness")
    print("Acousticness")
    print("Instrumentalness")
    print("Liveness")
    print("Valence")

    feature = input("Enter a song feature: ").lower().strip()

    high_low = input("High or low? ").lower().strip()

    artist_ids = []

    # get artist id
    (artist_id, artist_uri) = get_track_pool.get_artist_info(artist)

    # get related artists
    related_artists = get_track_pool.get_related_artist_ids(artist_uri)

    # get artist tracks
    artist_tracks = get_track_pool.get_artist_tracks(artist_id)

    # get audio features for artist tracks
    print("Getting track features for {}'s discography".format(artist))
    artist_track_features = get_track_pool.get_track_features(artist_tracks)

    # write to csv
    get_track_pool.write_to_csv(artist_track_features, related=False)

    # get track features for related artist tracks
    print("Getting related artist discographies")
    count = 1
    related_track_features = []
    for related_artist in related_artists:
        # get related artist tracks
        related_artist_tracks = get_track_pool.get_artist_tracks(related_artist[1])

        # get audio features for related artist tracks
        print("({}/20) Getting track features for {}'s discography".format(count, related_artist[0]))
        related_track_features.extend(get_track_pool.get_track_features(related_artist_tracks))
        count += 1

    # write related track features to csv
    get_track_pool.write_to_csv(related_track_features, related=True)

    # get list of matching tracks
    print("Determining cosine similarity based on {} {}".format(high_low, feature))
    analyse_track_pool.main(feature, high_low)

    playlist_name = artist + '_' + high_low + '_' + feature

    playlist_id = create_playlist.create_playlist(playlist_name)
    print("Created playlist {}".format(playlist_id))

    analysis_path = "{}/data/analysis.csv".format(os.path.dirname(os.path.realpath(__file__)))
    track_ids = create_playlist.read_csv(analysis_path)

    results = create_playlist.sp.user_playlist_add_tracks(create_playlist.username, playlist_id, track_ids)

    # TODO: clean up data folder
    data_path = get_track_pool.data_path
    shutil.rmtree(data_path)


if __name__ == '__main__':
    main()