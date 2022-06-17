from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from overall import Website as web
from profile import Profile as prof

# import spotipy as spot
# import sys


Builder.load_file('interface.kv')

class LoginPage(Screen):
    pass

class GenrePage(Screen):
    pass

class ArtistPage(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class MainWindow(StackLayout):
    
    # https://www.kaggle.com/datasets/zaheenhamidani/ultimate-spotify-tracks-db
    # CSV File from link above
    web_data = web('SpotifyFeatures.csv')
    df = web_data.get_data()
    user = prof(df)

    path_to_LP = None
    path_to_GP = None
    path_to_AP = None

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.path_to_LP = self.ids.loginPage.ids
        self.path_to_GP = self.ids.genrePage.ids
        self.path_to_AP = self.ids.artistPage.ids

    def get_user(self):
        return self.user

    def get_df(self):
        return self.df

    def set_username(self):
        self.user.set_name(self.path_to_LP.username.text)
        # print(self.user.get_name())
    
    def set_spotlink(self):
        self.user.set_spotlink(self.path_to_LP.link.text)
        # print(self.user.get_spotlink())
    
    def edit_genre_list(self, instance):
        if instance.background_color == [1.0, 0.0, 0.0, 1.0]:
            instance.background_color = 'green'
            self.user.add_top_genre(instance.text)
        else:
            instance.background_color = 'red'
            self.user.delete_top_genre(instance.text)
    
    def genreButtons(self):
        genres = (self.df.genre).unique()
        for genre in genres:
            cur_button = Button(text=genre, 
                                font_size=25,
                                size_hint=(.2, .147), 
                                background_color='red')
            cur_button.bind(on_press=self.edit_genre_list)
            self.path_to_GP.stack.add_widget(cur_button)

    def edit_artist_list(self, instance):
        if instance.background_color == [1.0, 0.0, 0.0, 1.0]:
            instance.background_color = 'green'
            self.user.add_top_artist(instance.text)
        else:
            instance.background_color = 'red'
            self.user.delete_top_artist(instance.text)

    def artist_search(self):
        entry = self.path_to_AP.searchEntry.text
        if len(entry) == 0: return
        search = self.user.searching(entry)
        layout = GridLayout(cols=1, rows=10)
        for result in search:
            cur_button = Button(text=result, 
                                font_size=25,
                                size_hint=(.2, .05), 
                                padding=(10,30),
                                background_color='red')
            cur_button.bind(on_press=self.edit_artist_list)
            layout.add_widget(cur_button)
        self.path_to_AP.searchResults.add_widget(layout)

    def clear_results(self):
        self.path_to_AP.searchResults.clear_widgets()
    
    pass

class myApp(MDApp):

    def build(self):
        return MainWindow()


if __name__ == "__main__":
    st = myApp()
    st.run()