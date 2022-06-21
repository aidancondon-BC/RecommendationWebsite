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
    personal_matrix = None
    personal_links = None
    df = None
    songThresholdReached = False
    
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

    def get_likes(self):
        return self.likes

    def get_dislikes(self):
        return self.dislikes

    def get_playlist(self):
        return self.playlist

    def get_personal_matrix(self):
        return self.personal_matrix

    def get_personal_links(self):
        return self.personal_links

    def get_df(self):
        return self.df

    def get_songThresholdReached(self):
        return self.songThresholdReached

    def set_name(self, name):
        self.name = name
    
    def set_spotlink(self, spotlink):
        self.spotlink = spotlink

    def set_personal_matrix(self, matrix):
        self.personal_matrix = matrix

    def set_personal_links(self, links):
        self.personal_links = links

    def set_df(self, df):
        self.df = df

    def set_songThresholdReached(self, isReached):
        self.songThresholdReached = isReached

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
    
    def add_liked_song(self, song):
        self.likes.append(song)
    
    def add_disliked_song(self, song):
        self.dislikes.append(song)

    def searching(self, word):
        word = word.lower()
        lw = len(word)
        rev_word = word[::-1]
        word_as_set = set(word)
        possible_searches = []
        for artist in self.df['artist_name'].unique():
            sim = 1 - (len((word_as_set - set(artist.lower()))) / lw)
            la = len(artist)
            rev_art = artist[::-1]
            for idx in range(min([lw,la])):
                if word[idx] == artist[idx]:
                    sim += 0.1
                if rev_word[idx] == rev_art[idx]:
                    sim += 0.1
            if sim >= 1.2: 
                possible_searches.append((artist, sim))
        searches = {}
        [searches.update({k:v}) for k,v in possible_searches]
        searches = sorted(searches, key=searches.get)
        searches.reverse()
        return searches[:10] if len(possible_searches) >= 10 else searches

    def songs_to_NOT_rec(self):
        songs_prob_not_like = []
        if len(self.dislikes) == 0: return []
        for song_index in self.dislikes:
            similiar_songs = list(enumerate(self.personal_matrix[song_index]))
            sorted_sim_songs = [x for x in similiar_songs if x[1] > 0.9]
            if len(sorted_sim_songs) == 0: continue
            songs_as_dict = {}
            [songs_as_dict.update({k:v}) for k,v in sorted_sim_songs]
            for song in list(songs_as_dict.keys()): 
                songs_prob_not_like.append(song)
        return songs_prob_not_like

    def songs_to_recommend(self):
        recommended_songs = []
        songs_prob_not_like = self.songs_to_NOT_rec()
        for song_index in self.likes:
            similiar_songs = list(enumerate(self.personal_matrix[song_index]))
            sorted_sim_songs = [x for x in similiar_songs if x[1] > 0.7]
            if len(sorted_sim_songs) == 0: continue
            for song in sorted_sim_songs:
                if song[0] in songs_prob_not_like or song[0] in self.likes: continue
                recommended_songs.append(song)
        return recommended_songs

    def make(self, web):
        songs_as_dict = {}
        [songs_as_dict.update({k:v}) for k,v in self.songs_to_recommend()]
        idxs = list(set(songs_as_dict.keys()))
        idxs.extend(self.likes)
        df_and_matrix = web.make_musical_matrix(idxs, self.df)
        df = df_and_matrix[0].reset_index(drop=True)
        matrix = df_and_matrix[1]
        possible_playlist_songs = []
        nums = 0
        lower = len(idxs) - len(self.likes)
        upper = len(idxs)
        for idx in range(lower, upper):
            sims = list(enumerate(matrix[idx]))
            possible_playlist_songs.extend(sims)
        possible = {}
        [possible.update({k:v}) for k,v in possible_playlist_songs]
        self.playlist = sorted(possible, key=possible.get)[:10]