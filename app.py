from kivymd.app import MDApp as App
from kivy.uix.image import Image, AsyncImage
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.graphics.context_instructions import Color
from kivy.graphics import Rectangle, Callback
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp
from kivymd.uix.card import MDSeparator, MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import BaseRectangularButton

from connection import search_for_device, Connection, Command
from screens.device_loading_screen import DeviceLoadingScreen 

import traceback
import favicon
import functools

from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '600')
Config.set('kivy', 'exit_on_escape', '0')
Config.write()

from kivy.core.window import Window
Window.clearcolor = (0.11, 0.11, 0.11, 1)


class PiPassApp(App):
    def build(self):
        self._connection = None
        self._screen_manager = ScreenManager()

        Window.bind(on_request_close=self.on_request_close)
        self.theme_cls.primary_palette = 'Gray'
        self.theme_cls.accent_palette = 'Red'
        self.theme_cls.theme_style = 'Dark'

        self._screen_manager.add_widget(DeviceLoadingScreen(name='device_loading_screen'))
        return self._screen_manager

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        if self._connection is None:
            self._connection = value

    @property
    def screen_manager(self):
        return self._screen_manager

    def on_request_close(self, *args):
        print('Exiting app..')
        self._connection.close()
        print('conn_open = {}'.format(self._connection.is_open()))
        self.textpopup(title='Exit', text='Are you sure?')
        
        return True

    def textpopup(self, title='', text=''):
        """Open the pop-up with the name"""
        box = MDBoxLayout(orientation='vertical')
        box.add_widget(MDLabel(text=text))
        mybutton = BaseRectangularButton(text='OK', size_hint=(1, 0.25))
        box.add_widget(mybutton)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        mybutton.bind(on_release=self.stop)
        popup.open()

if __name__ == "__main__":
    app = PiPassApp()
    try:
        app.run()
    except Exception as e:
        print(repr(e))
        print(''.join(traceback.format_exception(None, e, e.__traceback__)))
        if app.connection:
            app.connection.close()