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

    # only perform this on the artists that the user likes?
    def make_matrix_by_artists(self, artists):
        matrixs = []
        for artist in artists:
            cur_df = self.df.query('artist_name == @artist')
            cur_matrix = self.make_matrix(cur_df)
            matrixs.append(cur_matrix)
        return matrixs

    def make_matrix(self, dataFrame):
        genre = dataFrame[dataFrame.columns[0]]
        artist = dataFrame[dataFrame.columns[1]]
        key = dataFrame[dataFrame.columns[10]]
        mode = dataFrame[dataFrame.columns[13]]
        time_sig = dataFrame[dataFrame.columns[16]]
        dataFrame["merged_cols"] = artist + " " + genre + " " + key + " " + mode + " " + time_sig
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(dataFrame["merged_cols"])
        return cosine_similarity(count_matrix)

    def get_artist_top_songs(self, artist):
        tops = df.query('artist_name == @artist')
        tops = tops.sort_values(by=['popularity'], ascending=False)
        tops = tops['track_name'].unique()


    def get_data(self):
        return self.df

    