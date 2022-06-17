import numpy as np
import pandas as pd

class Profile:

    user_id = ""
    name = ""
    spotlink = ""
    top_artists = []
    top_genres = []
    likes = []
    reviewed = []
    dislikes = []
    playlist = []
    df = None
    
    def __init__(self, df):
        self.df = df

    def get_user_id(self):
        return self.user_id

    def get_name(self):
        return self.name

    def get_spotlink(self):
        return self.spotlink

    def get_top_artists(self):
        return self.top_artists

    def get_top_genres(self):
        return self.top_genres

    def set_name(self, name):
        self.name = name
    
    def set_spotlink(self, spotlink):
        self.spotlink = spotlink

    def add_top_artist(self, artist):
        self.top_artists.append(artist)

    def add_top_genre(self, genre):
        self.top_genres.append(genre)

    def delete_top_genre(self, genre):
        self.top_genres.remove(genre)
    
    def delete_top_artist(self, artist):
        self.top_artists.remove(artist)
    
    def set_top_genres(self, genres):
        self.top_genres = genres

    def searching(self, word):
        word = word.lower()
        lw = len(word)
        word_as_set = set(word)
        possible_searches = []
        for artist in self.get_artists_from_genres():
            sim = 1 - (len((word_as_set - set(artist.lower()))) / lw)
            la = len(artist)
            for idx in range(min([lw,la])):
                if word[idx] == artist[idx]:
                    sim += 0.1
            if sim >= 1.2: 
                possible_searches.append((artist, sim))
        searches = {}
        [searches.update({k:v}) for k,v in possible_searches]
        searches = sorted(searches, key=searches.get)
        searches.reverse()
        return searches[:10] if len(possible_searches) > 10 else searches
            
    
    def get_artists_from_genres(self):
        artists = []
        for g in self.get_top_genres():
            cur_artists = (self.df.query('genre == @g'))[self.df.columns[1]]
            artists.extend(cur_artists)
        return set(artists)

    def get_song(self, index):
        name = self.df.iloc[index][self.df.columns[2]]
        artist = self.df.iloc[index][self.df.columns[1]]
        return f'{name} by {artist}'        
    
    def songs_to_ask(self, matrix):
        songs = []
        for artist in self.top_artists:
            indexes = (self.df[self.df.artist_name == artist].index).to_numpy()
            for idx in indexes:
                similiar_songs = list(enumerate(matrix[idx]))
                sorted_sim_songs = np.array([x for x in similiar_songs if x[1] > 0.73])
                for song in sorted_sim_songs:
                    songs.append(song)
        return songs

    def ask_songs(self, matrix):
        songs = self.songs_to_ask(matrix)
        for song in songs:
            idx = int(song[0])
            song_name = self.get_song(idx)
            user_in = input(f'Do you like {song_name}? (Y/N/Q, then hit enter)\n')
            if user_in == 'Y': 
                self.likes.append(idx)
            if user_in == 'N': 
                self.dislikes.append(idx)
            if user_in == 'Q': break

    def songs_to_NOT_rec(self, matrix):
        songs_prob_not_like = []
        if len(self.dislikes) == 0: return []
        for song_index in self.dislikes:
            similiar_songs = list(enumerate(matrix[song_index]))
            sorted_sim_songs = [x for x in similiar_songs if x[1] > 0.9]
            if len(sorted_sim_songs) == 0: continue
            songs_as_dict = {}
            [songs_as_dict.update({k:v}) for k,v in sorted_sim_songs]
            for song in list(songs_as_dict.keys()): songs_prob_not_like.append(song)
        return songs_prob_not_like

    def songs_to_recommend(self, matrix):
        recommended_songs = []
        songs_prob_not_like = self.songs_to_NOT_rec(matrix)
        for song_index in self.likes:
            similiar_songs = list(enumerate(matrix[song_index]))
            sorted_sim_songs = [x for x in similiar_songs if x[1] > 0.7]
            if len(sorted_sim_songs) == 0: continue
            for song in sorted_sim_songs:
                if song[0] in songs_prob_not_like or song[0] in self.likes: continue
                recommended_songs.append(song)
        return recommended_songs

    def make(self, matrix):
        songs_as_dict = {}
        [songs_as_dict.update({k:v}) for k,v in self.songs_to_recommend(matrix)]
        playlist_length = 10
        tops = list(songs_as_dict.keys())
        np.random.shuffle(tops)
        playlist_created = sorted(set(tops[:playlist_length]))
        count = 0
        while len(playlist_created) != playlist_length:
            playlist_created.append(tops[len(tops) + count])
            playlist_created = sorted(set(playlist_created))
            count += 1
            print(count)
        self.playlist = playlist_created

    def print_playlist(self):
        for idx in self.playlist:
            print(self.get_song(int(idx)))