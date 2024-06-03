from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import pygame.mixer
import DB_Management as dbm
from pytube import YouTube, Search
import os

def add_random_recommendations(screen, amount, screen_manager):
    conn = dbm.create_connection()
    songsList = dbm.get_random_songs(conn, amount)
    for song in songsList:
        song_name, artist_name, album_name = song[3], song[1].replace(";", ", "), song[2]
        song_label = Label(text=f"[b][size=20]{song_name}[/size][/b]\n[size=14]{artist_name}[/size]", markup=True, halign='left', valign='middle', size_hint=(0.4, None), height=70, color=TEXT_COLOR)
        album_label = Label(text=album_name, halign='left', valign='middle', size_hint=(0.4, None), height=70, color=TEXT_COLOR)
        play_button = Button(text="Play", size_hint=(0.2, None), height=70, background_color=ACCENT_COLOR, color=TEXT_COLOR)
        play_button.bind(on_press=lambda instance, song_name=song_name: screen_manager.get_screen('downloader').enter_song_name(song_name))
        song_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=70)
        with song_layout.canvas.before:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=song_layout.pos, size=song_layout.size)
            Color(*BORDER_COLOR)
            Line(rectangle=(song_layout.x, song_layout.y, song_layout.width, song_layout.height), width=1)
        song_layout.add_widget(song_label)
        song_layout.add_widget(album_label)
        song_layout.add_widget(play_button)
        screen.add_widget(song_layout)
    conn.close()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box1vertical = BoxLayout(orientation='vertical', spacing=3)
        with self.box1vertical.canvas.before:
            Color(*PRIMARY_COLOR)
            Rectangle(pos=self.box1vertical.pos, size=self.box1vertical.size)

        self.box2horizontal = BoxLayout(spacing=3)
        self.boxcontent = BoxLayout(orientation='vertical', spacing=3)
        self.boxheader = BoxLayout(size_hint=(1, 0.2), spacing=3)
        self.playlists = ScrollView(size_hint=(0.3, 1))
        with self.playlists.canvas.before:
            Color(*BORDER_COLOR)
            Line(rectangle=(self.playlists.x, self.playlists.y, self.playlists.width, self.playlists.height), width=1)
        self.playlistBox = GridLayout(spacing=3, cols=1)
        self.scroll = ScrollView()
        self.b2 = BoxLayout(orientation='vertical', size_hint=(1, None), height=1060, spacing=3)
        self.search_results = BoxLayout(orientation='vertical', size_hint=(1, None), height=1060, spacing=3)
        self.searchAndHeader = BoxLayout(orientation='vertical')
        self.b5 = Button(size_hint=(0.2, 1), background_color=PRIMARY_COLOR, color=TEXT_COLOR)
        self.b5.id = 'profile'
        self.searchbarLayout = BoxLayout()
        self.labelHeader = Label(text='The main window of our music app!', color=TEXT_COLOR)
        self.searchBar = TextInput(text='Search for an artist or song', multiline=False, background_color=SECONDARY_COLOR, foreground_color=TEXT_COLOR)
        self.searchBar.id = 'searchBar'
        self.submitSearch = Button(text='Submit', size_hint=(0.2, 1), background_color=ACCENT_COLOR, color=TEXT_COLOR)
        self.submitSearch.bind(on_press=self.search)

        self.downloaderButton = Button(text='Downloader', size_hint=(0.2, 1), background_color=ACCENT_COLOR, color=TEXT_COLOR)
        self.downloaderButton.bind(on_press=self.switch_to_downloader)

        self.add_widget(self.box1vertical)
        self.box1vertical.add_widget(self.box2horizontal)
        self.box2horizontal.add_widget(self.playlists)
        self.playlists.add_widget(self.playlistBox)
        self.box2horizontal.add_widget(self.boxcontent)
        self.boxcontent.add_widget(self.boxheader)
        self.boxcontent.add_widget(self.scroll)
        self.scroll.add_widget(self.b2)
        self.boxheader.add_widget(self.searchAndHeader)
        self.boxheader.add_widget(self.b5)
        self.searchAndHeader.add_widget(self.labelHeader)
        self.searchAndHeader.add_widget(self.searchbarLayout)
        self.searchbarLayout.add_widget(self.searchBar)
        self.searchbarLayout.add_widget(self.submitSearch)
        self.searchbarLayout.add_widget(self.downloaderButton)
        self.b5.bind(on_press=self.switch_to_user_statistics)

        self.init_music_player()

        Clock.schedule_once(self.add_random_recommendations_callback, 0)

    def add_random_recommendations_callback(self, dt):
        add_random_recommendations(self.b2, 20, App.get_running_app().root)

    def init_music_player(self):
        pygame.mixer.init()

        self.music_player_layout = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(20), size_hint=(1, 0.4))

        left_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(None, 1), width=dp(200))
        with left_layout.canvas.before:
            Color(*BORDER_COLOR)
            Line(rectangle=(left_layout.x, left_layout.y, left_layout.width, left_layout.height), width=1)

        labels_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(30))
        self.current_song_label = Label(text='Drawings With Words', color=TEXT_COLOR)
        labels_layout.add_widget(self.current_song_label)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        previous_button = Button(text='<<', on_press=self.play_previous_song, size_hint=(None, None), width=dp(50), background_color=ACCENT_COLOR, color=TEXT_COLOR)
        play_pause_button = ToggleButton(text='Play', group='state', state='down', size_hint=(None, None), width=dp(50), background_color=ACCENT_COLOR, color=TEXT_COLOR)
        play_pause_button.bind(on_press=self.toggle_play_pause)
        next_button = Button(text='>>', on_press=self.play_next_song, size_hint=(None, None), width=dp(50), background_color=ACCENT_COLOR, color=TEXT_COLOR)
        buttons_layout.add_widget(previous_button)
        buttons_layout.add_widget(play_pause_button)
        buttons_layout.add_widget(next_button)

        self.queue_button = Button(text='Queue', size_hint=(None, None), width=dp(50), background_color=ACCENT_COLOR, color=TEXT_COLOR)
        self.queue_button.bind(on_press=self.open_file_chooser)
        buttons_layout.add_widget(self.queue_button)

        left_layout.add_widget(labels_layout)
        left_layout.add_widget(buttons_layout)

        right_layout = BoxLayout(orientation='horizontal', spacing=dp(20), size_hint=(1, None), height=dp(50))
        with right_layout.canvas.before:
            Color(*BORDER_COLOR)
            Line(rectangle=(right_layout.x, right_layout.y, right_layout.width, right_layout.height), width=1)
        self.start_time_label = Label(text='0:00', size_hint=(None, None), width=dp(50), color=TEXT_COLOR)
        self.song_progress_slider = Slider(min=0, max=100, size_hint=(1, None), height=dp(20))
        self.song_progress_slider.bind(on_touch_up=self.on_slider_touch_up)
        self.end_time_label = Label(text='3:18', size_hint=(None, None), width=dp(50), color=TEXT_COLOR)
        right_layout.add_widget(self.start_time_label)
        right_layout.add_widget(self.song_progress_slider)
        right_layout.add_widget(self.end_time_label)

        self.music_player_layout.add_widget(left_layout)
        self.music_player_layout.add_widget(right_layout)

        self.box1vertical.add_widget(self.music_player_layout)

        self.songs = ["walking.mp3"]
        self.current_index = 0
        self.is_paused = False

    def open_file_chooser(self, instance):
        filechooser = FileChooserListView(filters=['*.mp3'])
        filechooser.bind(on_selection=self.selected)

        popup = Popup(title='Select MP3 files', content=filechooser, size_hint=(0.9, 0.9))
        popup.open()

    def selected(self, filechooser, selection):
        if selection:
            self.songs = selection
            print(f"Updated queue: {self.songs}")

    def add_user_playlists(self, user_id):
        conn = dbm.create_connection()
        user_playlists = dbm.get_user_playlists(conn, user_id)
        conn.close()
        if user_playlists is None:
            print("No playlists available")
            return
        for playlist in user_playlists:
            playlist_button = Button(text=playlist[2], size_hint=(1, None), height=55, background_color=PRIMARY_COLOR, color=TEXT_COLOR)
            playlist_button.bind(on_press=lambda instance, pl_id=playlist[0]: self.show_playlist_tracks(pl_id))
            self.playlistBox.add_widget(playlist_button)

    def resize_box_layout(self, dt):
        scroll_box = self.scroll.children[0]
        total_height = sum(child.height for child in scroll_box.children)
        total_height += (len(scroll_box.children) - 1) * scroll_box.spacing
        total_height += scroll_box.padding[1] * 2
        self.search_results.height = total_height

    def search(self, instance):
        conn = dbm.create_connection()
        query = self.searchBar.text
        self.scroll.remove_widget(self.b2)
        self.scroll.remove_widget(self.search_results)
        results = dbm.search_bar(conn, query)
        self.search_results.clear_widgets()
        for song in results:
            song_name, artist_name, album_name = song[3], song[1].replace(";", ", "), song[2]
            song_label = Label(text=f"[b][size=20]{song_name}[/size][/b]\n[size=14]{artist_name}[/size]", markup=True, halign='left', valign='middle', size_hint=(0.4, None), height=70, color=TEXT_COLOR)
            album_label = Label(text=album_name, halign='left', valign='middle', size_hint=(0.4, None), height=70, color=TEXT_COLOR)
            play_button = Button(text="Play", size_hint=(0.2, None), height=70, background_color=ACCENT_COLOR, color=TEXT_COLOR)
            play_button.bind(on_press=lambda instance, song_name=song_name: self.manager.get_screen('downloader').enter_song_name(song_name))
            song_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=70)
            with song_layout.canvas.before:
                Color(*BACKGROUND_COLOR)
                Rectangle(pos=song_layout.pos, size=song_layout.size)
                Color(*BORDER_COLOR)
                Line(rectangle=(song_layout.x, song_layout.y, song_layout.width, song_layout.height), width=1)
            song_layout.add_widget(song_label)
            song_layout.add_widget(album_label)
            song_layout.add_widget(play_button)
            self.search_results.add_widget(song_layout)
        self.scroll.add_widget(self.search_results)
        conn.close()
        Clock.schedule_once(self.resize_box_layout, 0)

    def show_playlist_tracks(self, playlist_id):
        conn = dbm.create_connection()
        tracks = dbm.get_tracks_in_playlist(conn, playlist_id)
        conn.close()
        self.scroll.remove_widget(self.b2)
        self.scroll.remove_widget(self.search_results)
        self.b2.clear_widgets()
        for track in tracks:
            song_name, artist_name, album_name = track[3], track[1].replace(";", ", "), track[2]
            song_label = Label(text=f"[b][size=20]{song_name}[/size][/b]\n[size=14]{artist_name}[/size]", markup=True, halign='left', valign='middle', size_hint=(0.4, None), height=70, color=TEXT_COLOR)
            album_label = Label(text=album_name, halign='left', valign='middle', size_hint=(0.4, None), height=70, color=TEXT_COLOR)
            play_button = Button(text="Play", size_hint=(0.2, None), height=70, background_color=ACCENT_COLOR, color=TEXT_COLOR)
            play_button.bind(on_press=lambda instance, song_name=song_name: self.manager.get_screen('downloader').enter_song_name(song_name))
            track_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=70)
            with track_layout.canvas.before:
                Color(*BACKGROUND_COLOR)
                Rectangle(pos=track_layout.pos, size=track_layout.size)
                Color(*BORDER_COLOR)
                Line(rectangle=(track_layout.x, track_layout.y, track_layout.width, track_layout.height), width=1)
            track_layout.add_widget(song_label)
            track_layout.add_widget(album_label)
            track_layout.add_widget(play_button)
            self.b2.add_widget(track_layout)
        self.scroll.add_widget(self.b2)
        Clock.schedule_once(self.resize_box_layout, 0)

    def switch_to_user_statistics(self, instance):
        print("Switching to user statistics screen")
        self.manager.current = 'user_statistics'

    def switch_to_downloader(self, instance):
        print("Switching to YouTube downloader screen")
        self.manager.current = 'downloader'

    def on_pre_enter(self, *args):
        conn = dbm.create_connection()
        self.b5.text = str(dbm.get_username(conn, MusicApp.active_user))
        self.add_user_playlists(MusicApp.active_user)
        conn.close()

    def switch_to_player(self, instance):
        self.sm.current = 'player'

    def toggle_play_pause(self, instance):
        if instance.state == 'down':
            instance.text = 'Pause'
            if self.is_paused:
                pygame.mixer.music.unpause()
            else:
                self.play_music()
            self.is_paused = False
            Clock.schedule_interval(self.update_slider, 1)
        else:
            instance.text = 'Play'
            pygame.mixer.music.pause()
            self.is_paused = True
            Clock.unschedule(self.update_slider)

    def play_music(self):
        def play():
            pygame.mixer.music.load(self.songs[self.current_index])
            pygame.mixer.music.play()
            self.update_song_label()
            self.song_length = pygame.mixer.Sound(self.songs[self.current_index]).get_length()
            self.song_progress_slider.max = self.song_length
            self.song_progress_slider.value = 0

        Thread(target=play).start()

    def pause_music(self):
        pygame.mixer.music.pause()
        Clock.unschedule(self.update_slider)

    def play_next_song(self, instance):
        self.current_index = (self.current_index + 1) % len(self.songs)
        self.play_music()

    def play_previous_song(self, instance):
        self.current_index = (self.current_index - 1) % len(self.songs)
        self.play_music()

    def update_song_label(self):
        song_name = self.songs[self.current_index].split('.')[0]
        self.current_song_label.text = f'{song_name.replace("_", " ").title()}'
        self.artist_label.text = '3RDBURGLAR'

    def update_slider(self, dt):
        current_pos = pygame.mixer.music.get_pos() / 1000
        if not self.song_progress_slider.disabled:
            self.song_progress_slider.value = current_pos

        self.start_time_label.text = self.format_time(current_pos)
        remaining_time = self.song_length - current_pos
        self.end_time_label.text = self.format_time(remaining_time)

    def on_slider_touch_up(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.song_progress_slider.disabled = False
            self.seek_music(self.song_progress_slider.value)

    def seek_music(self, slider_value):
        pygame.mixer.music.rewind()
        pygame.mixer.music.set_pos(slider_value)
        if not self.is_paused:
            pygame.mixer.music.play(start=slider_value)

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f'{mins}:{secs:02d}'

class UserStatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.user_id = None
        self.box.add_widget(Label(text='User Statistics', color=TEXT_COLOR))
        self.stats_label = Label(color=TEXT_COLOR)
        self.box.add_widget(self.stats_label)
        self.update_button = Button(text='Update Statistics', background_color=PRIMARY_COLOR, color=TEXT_COLOR)
        self.update_button.bind(on_press=self.update_stats)
        self.box.add_widget(self.update_button)
        self.add_widget(self.box)

        self.back_button = Button(text="Back", size_hint=(0.2, 0.1), background_color=PRIMARY_COLOR, color=TEXT_COLOR)
        self.back_button.bind(on_press=self.go_back)
        self.box.add_widget(self.back_button)

    def on_pre_enter(self, *args):
        print("Entering UserStatisticsScreen")
        self.user_id = MusicApp.active_user
        print(f"Active user ID: {self.user_id}")
        self.update_content()

    def update_stats(self, *args):
        self.update_content()

    def update_content(self, *args):
        if self.user_id is None:
            print("No active user ID found")
            self.stats_label.text = 'No user logged in.'
            return
        conn = dbm.create_connection()
        stats = dbm.get_user_statistics(conn, self.user_id)
        print(f"Retrieved stats: {stats}")
        if stats:
            self.stats_label.text = f'Most Listened Artist: {stats[1]}\n' \
                                    f'Favorite Genre: {stats[2]}\n' \
                                    f'Total Time Listened: {stats[3]} minutes'
        else:
            self.stats_label.text = 'No statistics available.'
        conn.close()

    def go_back(self, instance):
        self.manager.current = 'main'

class WelcomeScreen(Screen):
    pass

class LogInScreen(Screen):
    def get_username_and_password(self):
        username = self.ids.log_in_username.text
        password = self.ids.log_in_password.text

        conn = dbm.create_connection()
        if dbm.user_exists(conn, username, password):
            MusicApp.active_user = dbm.get_user_id(conn, username)
            conn.close()
            MusicApp.on_login_success()
            return True

        print("This user doesn't exist!")
        conn.close()
        return False

class SignUpScreen(Screen):
    def month_spinner_clicked(self, value):
        self.ids.sign_up_month.text = value

    def day_spinner_clicked(self, value):
        self.ids.sign_up_day.text = value

    def create_new_user(self):
        username = self.ids.sign_up_username.text
        password1 = self.ids.sign_up_password1.text
        password2 = self.ids.sign_up_password2.text
        birthdate = self.ids.sign_up_year.text + "-" + self.ids.sign_up_month.text + "-" + self.ids.sign_up_day.text

        conn = dbm.create_connection()
        if dbm.username_exists(conn, username):
            print("Username exists!")
            conn.close()
            return False

        if password1 != password2:
            print("Passwords must match!")
            conn.close()
            return False

        dbm.add_user(conn, username, password1, birthdate)
        conn.commit()

        MusicApp.active_user = dbm.get_user_id(conn, username)
        conn.close()
        MusicApp.on_signup_success()
        return True

class YouTubeDownloaderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = get_color_from_hex('#2C3E50')

        self.box_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.url_input = TextInput(hint_text='Enter YouTube URL', size_hint=(1, 0.1), background_color=get_color_from_hex('#34495E'), foreground_color=get_color_from_hex('#ECF0F1'))
        self.box_layout.add_widget(self.url_input)

        self.keyword_input = TextInput(hint_text='Enter keyword to search', size_hint=(1, 0.1), background_color=get_color_from_hex('#34495E'), foreground_color=get_color_from_hex('#ECF0F1'))
        self.box_layout.add_widget(self.keyword_input)

        self.search_button = Button(text='Search', size_hint=(1, 0.1), background_color=get_color_from_hex('#1ABC9C'), color=get_color_from_hex('#ECF0F1'))
        self.search_button.bind(on_press=self.search_videos)
        self.box_layout.add_widget(self.search_button)

        self.search_results = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.search_results.bind(minimum_height=self.search_results.setter('height'))
        self.scroll_view = ScrollView(size_hint=(1, 0.5), bar_width=10, scroll_type=['bars'], bar_color=get_color_from_hex('#1ABC9C'))
        self.scroll_view.add_widget(self.search_results)
        self.box_layout.add_widget(self.scroll_view)

        self.download_mp3_button = Button(text='Download as MP3', size_hint=(1, 0.1), background_color=get_color_from_hex('#3498DB'), color=get_color_from_hex('#ECF0F1'))
        self.download_mp3_button.bind(on_press=self.download_as_mp3)
        self.box_layout.add_widget(self.download_mp3_button)

        self.download_mp4_button = Button(text='Download as MP4', size_hint=(1, 0.1), background_color=get_color_from_hex('#E74C3C'), color=get_color_from_hex('#ECF0F1'))
        self.download_mp4_button.bind(on_press=self.download_as_mp4)
        self.box_layout.add_widget(self.download_mp4_button)

        self.add_widget(self.box_layout)

        self.back_button = Button(text="Back", size_hint=(1, 0.1), background_color=PRIMARY_COLOR, color=TEXT_COLOR)
        self.back_button.bind(on_press=self.go_back)
        self.box_layout.add_widget(self.back_button)

    def enter_song_name(self, song_name):
        self.keyword_input.text = song_name
        self.manager.current = 'downloader'

    def search_videos(self, instance):
        keyword = self.keyword_input.text
        search = Search(keyword)
        self.videos = search.results
        self.search_results.clear_widgets()

        for video in self.videos:
            video_button = Button(text=video.title, size_hint_y=None, height=40, background_color=get_color_from_hex('#34495E'), color=get_color_from_hex('#ECF0F1'))
            video_button.bind(on_press=lambda btn, v=video: self.select_video(v))
            self.search_results.add_widget(video_button)

    def select_video(self, video):
        self.selected_video = video
        self.url_input.text = video.watch_url

    def download_as_mp3(self, instance):
        url = self.url_input.text
        if url:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            out_file = stream.download()
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            print(f'Downloaded {new_file}')

    def download_as_mp4(self, instance):
        url = self.url_input.text
        if url:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream.download()
            print(f'Downloaded {yt.title}.mp4')

    def go_back(self, instance):
        self.manager.current = 'main'

class MusicApp(App):
    active_user = None

    def build(self):
        sm = ScreenManager()

        welcome_screen = WelcomeScreen(name='welcome')
        sm.add_widget(welcome_screen)
        login_screen = LogInScreen(name='log_in')
        sm.add_widget(login_screen)
        signup_screen = SignUpScreen(name='sign_up')
        sm.add_widget(signup_screen)

        main_screen = MainScreen(name='main')
        main_screen.disabled = True
        sm.add_widget(main_screen)

        user_stats_screen = UserStatisticsScreen(name='user_statistics')
        sm.add_widget(user_stats_screen)

        downloader_screen = YouTubeDownloaderScreen(name='downloader')
        sm.add_widget(downloader_screen)

        sm.current = 'welcome'

        return sm

    @staticmethod
    def on_login_success():
        sm = App.get_running_app().root
        if 'main' in sm.screen_names:
            main_screen = sm.get_screen('main')
            main_screen.disabled = False
            sm.current = 'main'

    @staticmethod
    def on_signup_success():
        sm = App.get_running_app().root
        if 'main' in sm.screen_names:
            main_screen = sm.get_screen('main')
            main_screen.disabled = False
            sm.current = 'main'

MusicApp().run()
