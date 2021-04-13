from kivymd.app import MDApp as App
from kivy.uix.widget import Widget
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDSeparator, MDCard
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget, IconLeftWidget
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


class CredentialField(MDTextField):
    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        self.encrypted = kwargs.pop('encrypted', False)
        self.parent_credential = kwargs.pop('parent_credential', None)
        self.font_size = "12sp"
        self.font_size_hint_text = 12
        self.font_name = './res/fonts/NotoSans-Regular.ttf'
        self.font_name_hint_text = './res/fonts/NotoSans-Regular.ttf'
        super().__init__(**kwargs)
        self.line_color_normal = App.get_running_app().theme_cls.accent_color
        # self.hint_text = kwargs.get('hint_text', 'Field')
        self.disabled = True

        if self.encrypted:
            self.password_mask = "\u2022"
            self.text = self.hint_text or "_default_"
            self.password = True
            self.icon_right = 'eye-off'

    def set_hint_text(self, value):
        self.hint_text = value.capitalize()


    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.icon_right:
                icon_x = (self.width + self.x) - (self._lbl_icon_right.texture_size[1]) - dp(8)
                icon_y = self.center[1] - self._lbl_icon_right.texture_size[1] / 2
                if self.mode == "rectangle":
                    icon_y -= dp(4)
                elif self.mode != 'fill':
                    icon_y += dp(8)

                if touch.pos[0] > icon_x and touch.pos[1] > icon_y:
                    if self.password:
                        print(self.parent_credential, self.hint_text)
                        if self.parent_credential and self.hint_text:
                            self.app.connection.bind(
                                on_receive=self.reveal_credential_info,
                                type=Command.Types.ENCRYPTED_FIELD_VALUE
                            )
                            self.app.connection.send_encrypted_field_value(
                                self.parent_credential,
                                self.hint_text.lower()
                            )
                    else:
                        self.text = self.hint_text if self.hint_text else '_default_'
                        self.password = True
                        self.icon_right = 'eye-off'

                    # try to adjust cursor position
                    cursor = self.cursor
                    self.cursor = (0,0)
                    Clock.schedule_once(functools.partial(self.set_cursor, cursor))
        return super(CredentialField, self).on_touch_down(touch)

    def reveal_credential_info(self, reply):
        print('in reveal credneital')
        self.app.connection.unbind(Command.Types.ENCRYPTED_FIELD_VALUE)
        self.text = reply['options']
        self.icon_right = 'eye'
        self.password = False

    def set_cursor(self, pos, dt):
        self.cursor = pos

class MainScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.app.connection.bind(on_receive=self.received_load_credentials, type=Command.Types.LIST_CREDENTIALS)

        self.app.connection.send_list_credentials()


    def received_load_credentials(self, reply):
        for name in reply['options']:
            self.add_credential(name, 'https://gitlab.com')

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
            
    def show_credential_details(self, reply):
        self.app.connection.unbind(Command.Types.CREDENTIAL_DETAILS)
        self.ids.details_layout.clear_widgets()
        for k,v in reply['options'].items():
            cr = CredentialField(text=v or '', encrypted=(v is None), parent_credential=self._last_pressed_credential.text)
            cr.set_hint_text(k)
            self.ids.details_layout.add_widget(cr)
        