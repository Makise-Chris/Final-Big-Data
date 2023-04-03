import os
import spotipy
import json
import pandas as pd
import re
from spotipy.oauth2 import SpotifyClientCredentials


class MySpotify(object):
    """This class was to download data from Spotify API.
    The download process should be: 
        artist=artist_genre -> album=album_artists(artist) -> songs=songs_albums(album)
    
    """
    def __init__(self,genre='k-pop'):
        self.authenticate()
        self.genre=genre
        
        
    def authenticate(self):
        my_id = '8d537c4e09064dd0b58e0d0b80d87630'
        secret_key = '76f50edef5704a20be49178b4528b8e2'
        
        client_credentials_manager = SpotifyClientCredentials(client_id = my_id, client_secret = secret_key)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                
        
    def artist_genre(self):
        """Download all artists info from a genre """
        
        artist=[]
        #at=self.sp.search(q='genre:'+self.genre,limit=50,type='artist')['artists']
        
        for i in range(0,1000,50):
            artist+=self.sp.search(q='genre:'+self.genre,limit=50,type='artist',offset=i)['artists']['items']
        #save_json("data/artists/{}_artists_info".format(self.genre),artist)
        print("Download {}'s artists info".format(self.genre))
        print()
                
        return artist
    
    def album_artists(self):
        """Download all albums info from artists """
        artist=open_json("data/artists/{}_artists_info".format(self.genre))
        album={}
        
        for i in artist:
            name=i['name']
            album[name]=[]
            ab=self.sp.artist_albums(i['id'], limit=50)
            
            if ab['total']>50:
                for j in range(0,ab['total'],50):
                    album[name]+=self.sp.artist_albums(i['id'], limit=50,offset=j)['items']
            else:
                album[name]+=self.sp.artist_albums(i['id'], limit=50)['items']
            print("Download {}'s albums info".format(name))
        save_json("data/full_albums_of_all_artists/{}_albums_info".format(self.genre),album)
        
        return album

    def album_by_artists(self, id):
        albums = []
        ab = self.sp.artist_albums(id, limit=50)

        if ab['total'] > 50:
            for j in range(0, ab['total'], 50):
                albums += self.sp.artist_albums(
                    id, limit=50, offset=j)['items']
        else:
            albums += self.sp.artist_albums(
                id, limit=50)['items']
        return albums

    def album_artists_split(self):
        """Download all albums info from artists """
        artist=open_json("data/artists/{}_artists_info".format(self.genre))
        album={}
        
        for i in artist:
            list_dir=os.listdir('./data/albums/')
            name=i['name']
            name=name.replace('/','_')
            name=name.replace('*','_')
            if "{}albums.json".format(name) not in list_dir:
                album[name]=[]
                ab=self.sp.artist_albums(i['id'], limit=50)
                
                if ab['total']>50:
                    for j in range(0,ab['total'],50):
                        album[name]+=self.sp.artist_albums(i['id'], limit=50,offset=j)['items']
                else:
                    album[name]+=self.sp.artist_albums(i['id'], limit=50)['items']
                print("Download {}'s albums info".format(name))
                save_json("data/albums/{}_albums_info".format(name),album[name])
        
        return album
    
    def songs_albums(self):  
        """Download all songs info from albums """
        album=open_json("data/full_albums_of_all_artists/{}_albums_info".format(self.genre))
        
        songs={}
        
        for k,v in album.items():
            list_dir=os.listdir('./data/tracks/')
            k=k.replace('/','_')
            
            if "{}_tracks_info.json".format(k) not in list_dir:
                songs['artist']=k
                songs['albums']={}
                
                for i in v:        
                    songs['albums'][i['id']]=self.sp.album_tracks(i['id'])['items']
                save_json("data/tracks/{}_tracks_info".format(k),songs)
                print("Download {}'s tracks info".format(k))
                
        return songs

    def songs_albums(self, id):
        """Download all songs info from albums """
        songs = []
        # self.sp.album_tracks(i['id'])['items']
        ab = self.sp.album_tracks(id, limit=50)

        if ab['total'] > 50:
            for j in range(0, ab['total'], 50):
                songs += self.sp.album_tracks(
                    id, limit=50, offset=j)['items']
        else:
            songs += self.sp.album_tracks(
                id, limit=50)['items']
        return songs

    def songs_albums_add_popularity(self):
        list_dir=os.listdir('./data/tracks/')
        
        for fl in list_dir:
            try:
                album=open_json("data/tracks/{}".format(fl[:-5]))
            except:
                pass
            for ak,av in album['albums'].items():
                for tr in av:
                    try:
                        tr['popularity']=self.sp.track(tr['id'])['popularity']
                    except Exception as e:
                        print(e,album['artist'])
            print("Add track popularity to {}'s songs".format(album['artist']))
            save_json("data/tracks/{}".format(fl[:-5]),album)
        
def update_data(genre='k-pop'):
    spf=MySpotify(genre)  
    #upate artists info 
    artist=spf.artist_genre()
    #update albums info of artists
    album=spf.album_artists(artist)
    #update songs info of albums
    spf.songs_albums(album)


def save_json(name,dt):
    with open('./%s.json'%name,'w') as f:
        json.dump(dt,f)


def open_json(name):
    with open('./%s.json'%name,'r') as f:
        dt=json.load(f)
    return dt


if __name__=="__main__":
   
    #spotf=MySpotify()
        
    pass