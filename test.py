from kafka import KafkaProducer
import SpotifyGetData
import pickle
import time
import json

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

spotipyGetData = SpotifyGetData.MySpotify()

artists = spotipyGetData.artist_genre()
i = 0
for artist in artists:
    id = artist['id']
    print(id)
    albums = spotipyGetData.album_by_artists(id)
    for album in albums:
        id_album = album['id']
        print(id_album)
        tracks = spotipyGetData.songs_albums(id_album)
        for track in tracks:
            i = i+1
            print(i)
            print(track['id'])
            print('--------------------------------------------------------------')
