import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial import distance
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import OrdinalEncoder

class Website:

    file_name = None
    df = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.df = pd.read_csv(self.file_name, engine='pyarrow')

    def condense_df(self, cur_df, fav_genres):
        songs_per_fav = int(5000 / len(fav_genres))
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
        cur_df = cur_df.drop_duplicates(subset=['artist_name','track_name'])
        cur_df = cur_df.reset_index(drop=True)
        return self.make_matrix(cur_df)

    def make_matrix(self, dataFrame):
        genre = dataFrame['genre'] + ' '
        artist = dataFrame['artist_name'] + ' '
        key = dataFrame['key'] + ' '
        mode = dataFrame['mode'] + ' '
        time_signature = dataFrame['time_signature'] + ' '
        dataFrame['merged_cols'] = genre + artist + key + mode + time_signature
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(dataFrame['merged_cols'])
        return [dataFrame, cosine_similarity(count_matrix)]

    def musical_matrix(self, dataFrame):
        nums = dataFrame.values
        matrix = distance.cdist(nums, nums, 'euclidean')
        return matrix

    def giveDfPredictions(self, dataFrame):
        df_w_revs = dataFrame[dataFrame['Review'].notna()]
        all_df = dataFrame
        features = ["genre","artist_name","popularity","acousticness","danceability","duration_ms","energy","instrumentalness","key","liveness","loudness","mode","speechiness","tempo","time_signature","valence"]
        to_predict = all_df[features]
        X = df_w_revs[features]
        y = df_w_revs.Review
        s = (X.dtypes == 'object')
        object_cols = list(s[s].index)
        label_X = X.copy()
        label_TP = to_predict.copy()
        label_X[object_cols] = OrdinalEncoder().fit_transform(X[object_cols])
        label_TP[object_cols] = OrdinalEncoder().fit_transform(to_predict[object_cols])
        K = int(df_w_revs.shape[0] ** 0.5)
        model = KNeighborsRegressor(n_neighbors=K, metric='euclidean')
        model.fit(label_X, y)
        predictions = model.predict(label_TP)
        dataFrame['Predictions'] = None
        for i in range(dataFrame.shape[0]):
            dataFrame.at[i, 'Predictions'] = predictions[i]
        return dataFrame
        

    def get_artist_top_songs(self, artist):
        tops = self.df.query('artist_name == @artist')
        tops = tops.sort_values(by=['popularity'], ascending=False)
        tops = tops['track_name'].unique()
        return tops if len(tops) <= 10 else tops[:10]

    def get_data(self):
        return self.df