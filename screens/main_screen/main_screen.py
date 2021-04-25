from kivymd.app import MDApp as App
from kivy.uix.widget import Widget
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.card import MDSeparator, MDCard
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget, IconLeftWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRectangleFlatButton, BaseFlatButton
from kivy.uix.togglebutton import ToggleButtonBehavior, ToggleButton
from kivy.uix.button import Button
from screens.main_screen.components.body import CredentialInformationBody, AddCredentialBody
from screens.main_screen.components.fields import CredentialField
from screens.main_screen.components.footer import CredentialInformationFooter, AddCredentialFooter


import functools

from connection import Command
import favicon
import requests
import glob
import re


class BaseShadowWidget(Widget):
    pass

class ElevatedGridLayout(RectangularElevationBehavior, BaseShadowWidget, MDGridLayout):
    pass

class TypeToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.size = 30, 30
        self.group = "type"


class MainScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
        self.body = CredentialInformationBody()
        self.footer = MDStackLayout()
        self.ids.body_layout.add_widget(self.body)
        self.ids.footer_layout.add_widget(self.footer)

        self.app.connection.bind(on_receive=self.received_load_credentials, type=Command.Types.LIST_CREDENTIALS)
        self.app.connection.send_list_credentials()


    def received_load_credentials(self, reply):
        for credential in reply['options']:
            self.add_credential(credential['name'], credential['url'])

    @functools.lru_cache()
    def get_credential_icon(self, url):
        try:
            image_path_base = re.sub(r'http.://', '', url)
            paths = glob.glob('./res/icons/{}.*'.format(image_path_base))
            if len(paths) > 0:
                return paths[0]
            
            icon = list(filter(lambda x: x.format in ['ico', 'png'], favicon.get(url)))[0]

            response = requests.get(icon.url, stream=True)
            with open('./res/icons/{}.{}'.format(image_path_base, icon.format), 'wb') as image:
                for chunk in response.iter_content(1024):
                    image.write(chunk) 

            return './res/icons/{}.{}'.format(image_path_base, icon.format)
        except:
            return'./res/img/locked.png'

    def add_credential(self, name=None, url=None):
        icon_path = self.get_credential_icon(url)

        entry = TwoLineAvatarListItem( text= name,
                            secondary_text=name)

        entry.add_widget(ImageLeftWidget(source=icon_path))
        entry.bind(on_release=self.ask_for_credential_details)

        self.ids.credential_list.add_widget(MDSeparator())
        self.ids.credential_list.add_widget(entry)


    def ask_for_credential_details(self, instance):
        if not self.app.connection.is_bound(Command.Types.CREDENTIAL_DETAILS):
            self.app.connection.bind(on_receive=self.show_credential_details, type=Command.Types.CREDENTIAL_DETAILS)
            self.app.connection.send_credential_details(instance.text)
            self._last_pressed_credential = instance

    def send_add_credential(self, *args):
        if isinstance(self.footer, AddCredentialFooter) and isinstance(self.body, AddCredentialBody):
            form_information = self.body.get_form_information()
            self.app.connection.send_add_credential(form_information)
            
    def show_credential_details(self, reply):
        self.app.connection.unbind(Command.Types.CREDENTIAL_DETAILS)
        self.change_to_information_body()

        for k,v in reply['options'].items():
            cr = CredentialField(text=v or '', encrypted=(v is None), parent_credential=self._last_pressed_credential.text)
            cr.set_hint_text(k)
            self.body.ids.details_layout.add_widget(cr)

    def change_to_information_body(self):
        self.ids.body_layout.remove_widget(self.body)
        self.body = CredentialInformationBody()
        self.ids.body_layout.add_widget(self.body)

        self.ids.footer_layout.remove_widget(self.footer)
        self.footer = CredentialInformationFooter()
        self.ids.footer_layout.add_widget(self.footer)

    def change_to_add_credential_body(self):
        if isinstance(self.body, CredentialInformationBody):
            self.ids.body_layout.remove_widget(self.body)
            self.body = AddCredentialBody()
            self.ids.body_layout.add_widget(self.body)

            self.ids.footer_layout.remove_widget(self.footer)
            self.footer = AddCredentialFooter(on_save=self.send_add_credential)
            self.ids.footer_layout.add_widget(self.footer)

        