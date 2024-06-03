from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty
import os

class SelectableRecycleBoxLayout(FocusBehavior, RecycleBoxLayout):
    pass

class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

class MusicQueueApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical')
        
        self.queue_rv = RecycleView(size_hint=(1, 0.8))
        self.queue_rv.viewclass = 'SelectableLabel'

        # Integrate the layout manager as a child of the RecycleView
        layout_manager = SelectableRecycleBoxLayout(orientation='vertical')
        self.queue_rv.add_widget(layout_manager)
        self.queue_rv.layout_manager = layout_manager

        self.root.add_widget(self.queue_rv)

        add_button = Button(text='Add Music', size_hint=(1, 0.1))
        add_button.bind(on_press=self.add_music_to_queue)
        self.root.add_widget(add_button)

        print_queue_button = Button(text='Print Queue', size_hint=(1, 0.1))
        print_queue_button.bind(on_press=self.print_queue)
        self.root.add_widget(print_queue_button)

        self.current_song_label = Label(text='Current Song:', size_hint=(1, 0.05))
        self.root.add_widget(self.current_song_label)

        self.current_song_details_label = Label(text='', size_hint=(1, 0.05))
        self.root.add_widget(self.current_song_details_label)

        return self.root

    def add_music_to_queue(self, instance):
        self.selected_music_files = []  # Store selected music files
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['.mp3', '.wav', '*.ogg'], size_hint=(1, 1))
        content.add_widget(filechooser)
        
        button_layout = BoxLayout(size_hint=(1, 0.2))
        select_button = Button(text='Select')
        select_button.bind(on_release=lambda x: self.on_file_chooser_submit(filechooser.selection))
        close_button = Button(text='Close')
        close_button.bind(on_release=lambda x: self.popup.dismiss())
        
        button_layout.add_widget(select_button)
        button_layout.add_widget(close_button)
        
        content.add_widget(button_layout)

        self.popup = Popup(title='Select Music Files', content=content, size_hint=(None, None), size=(600, 600))
        self.popup.open()

    def on_file_chooser_submit(self, selection):
        for music_file in selection:
            music_file_name = os.path.basename(music_file)
            self.selected_music_files.append(music_file_name)  # Store selected music files
        # Don't add files to queue immediately, wait until the popup is closed
        # self.queue_rv.data.append({'text': music_file_name})
        # self.queue_rv.refresh_from_data()

    def print_queue(self, instance):
        print("Current Music Queue:")
        for item in self.selected_music_files:
            print(item)

if __name__ == '_main_':
    MusicQueueApp().run()