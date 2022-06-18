import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

class Website:

    file_name = None
    df = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.df = pd.read_csv(self.file_name, engine='pyarrow')

    def condense_df(self, cur_df, fav_genres):
        songs_per_fav = int(2000 / len(fav_genres))
        for fav in fav_genres:
            fav_df = cur_df.query('genre == @fav')
            fav_df = fav_df.sort_values(by=['popularity'], ascending=False)
            if fav_df.shape[0] <= songs_per_fav: 
                continue
            else:
                idxs = list(fav_df.index)[songs_per_fav:]
                cur_df = cur_df.drop(idxs)
        return cur_df

    def specify_df(self, fav_artists, fav_genres):
        art_df = self.df[self.df['artist_name'].isin(fav_artists)]
        gen_df = self.df[self.df['genre'].isin(fav_genres)]
        return pd.concat([art_df, gen_df]).drop_duplicates()


    def make_matrix_by_genres(self, fav_artists, fav_genres):
        cur_df = self.specify_df(fav_artists, fav_genres)
        if cur_df.shape[0] > 10000:
            cur_df = self.condense_df(cur_df, fav_genres)
        return self.make_matrix(cur_df.reset_index(drop=True))

    def make_matrix(self, dataFrame):
        genre = dataFrame[dataFrame.columns[0]]
        artist = dataFrame[dataFrame.columns[1]]
        key = dataFrame[dataFrame.columns[10]]
        mode = dataFrame[dataFrame.columns[13]]
        time_sig = dataFrame[dataFrame.columns[16]]
        dataFrame["merged_cols"] = artist + " " + genre + " " + key + " " + mode + " " + time_sig
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(dataFrame["merged_cols"])
        return [dataFrame, cosine_similarity(count_matrix)]

    def get_artist_top_songs(self, artist):
        tops = self.df.query('artist_name == @artist')
        tops = tops.sort_values(by=['popularity'], ascending=False)
        tops = tops['track_name'].unique()
        return tops if len(tops) <= 10 else tops[:10]

    def get_data(self):
        return self.df