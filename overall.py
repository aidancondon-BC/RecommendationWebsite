import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

pd.options.display.max_rows = 9999

class Website:

    file_name = None
    df = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.df = pd.read_csv(self.file_name, engine='pyarrow')

    def condense_df(self, cur_df, col_name, favs):
        songs_per_fav = int(10000 / len(favs))
        for fav in favs:
            fav_df = cur_df.query('genre == @fav')
            fav_df = fav_df.sort_values(by=['popularity'], ascending=False)
            idxs = list(fav_df.index)[:songs_per_fav]
            if fav_df.shape[0] <= songs_per_fav: 
                print(fav_df.shape[0])
                continue
            else:
                cur_df.drop(index=idxs)
        return cur_df

    def make_matrix_by_genres(self, col_name, user_favs_from_col):
        cur_df = self.df[self.df[col_name].isin(user_favs_from_col)]
        #if cur_df.shape[0] > 10000:
        #    cur_df = self.condense_df(cur_df, col_name, user_favs_from_col)
        return self.make_matrix(cur_df)

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