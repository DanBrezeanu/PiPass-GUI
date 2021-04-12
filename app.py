from kivymd.app import MDApp as App
from kivy.uix.image import Image, AsyncImage
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.graphics.context_instructions import Color
from kivy.graphics import Rectangle, Callback
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget, IconLeftWidget
from kivymd.uix.card import MDSeparator, MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.textfield import MDTextField

from connection import search_for_device, Connection, Command

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

sm = ScreenManager()
conn = None

class DeviceLoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_status = False
        Clock.schedule_interval(lambda *args: search_for_device(self.get_device_status), 1)
    
    def get_device_status(self, status):
        global conn
        # print(status)
        if self.device_status == False and status == True:
            if conn is None:
                conn = Connection()
                conn.bind(self.received_hello, Command.Types.APP_HELLO)
                print('Connection up')
                print(conn)
                conn.send_app_hello()

        elif self.device_status == True and status == False:
            sm.clear_widgets()
            sm.add_widget(DeviceLoadingScreen(name='device_loading'))
            sm.current = 'device_loading'

        self.device_status = status

    def received_hello(self, reply):
        print('Got hello reply')
        conn.unbind(Command.Types.APP_HELLO)

        if reply['options'] == '1':
            sm.add_widget(PinScreen(name='pin_screen'))
            sm.current = 'pin_screen'
        else:
            print("DEVICE LOCKED")
            sm.add_widget(DeviceLockedScreen(name='locked_screen'))
            sm.current = 'locked_screen'

class DeviceLockedScreen(Screen):
    class PasswordPopup(Popup):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self._on_dismiss_bind_callback = kwargs.get('on_dismiss_bind_callback', None)
            content = BoxLayout(orientation='vertical', spacing=5,padding=(30,30,30,30))

            content.add_widget(
                Label(
                    text='Enter the password to unlock the device',
                    pos_hint = {'center_x': .5, 'center_y': .5},
                    halign='center'
                )
            )

            text_input = TextInput(
                multiline=False,
                password=True,
                size_hint=(1, 0.2),
                background_color=(0.11, 0.11, 0.11, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1),
            )
            content.add_widget(text_input)

            content.add_widget(
                Button(
                    text='OK',
                    size_hint=(1, 0.3),
                    on_release=lambda *args: conn.send_password(text_input.text)
                )
            )

            content.add_widget(
                Button(
                    text='Cancel',
                    size_hint=(1, 0.3),
                    on_release=self.dismiss
                )
            )

            self.content = content
         

        def dismiss(self, *args, **kwargs):
            super().dismiss(*args, **kwargs)
            conn.bind(
                on_receive=self._on_dismiss_bind_callback,
                type=Command.Types.ASK_FOR_PASSWORD,
            )

            

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        conn.bind(on_receive=self.received_hello, type=Command.Types.APP_HELLO)
        conn.bind(on_receive=self.received_ask_for_password, type=Command.Types.ASK_FOR_PASSWORD)
        self.ids.try_again_button.bind(
            on_press=lambda *args: conn.send_app_hello()
        )
        
    def received_hello(self, reply):
        if reply['options'] == '1':
            conn.unbind(Command.Types.APP_HELLO)
            sm.add_widget(PinScreen(name='pin_screen'))
            sm.current = 'pin_screen'
        else:
            initial_pos = self.ids.locked_img.x
            initial_pos_y = self.ids.locked_img.y
            print(initial_pos, self.ids.locked_img)
            # TODO: make this work
            anim = Animation(pos=(initial_pos + 50, initial_pos_y+ 50), duration=.5, t='out_bounce') + \
                   Animation(pos=(initial_pos + 50, initial_pos_y+ 50), duration=.1, t='out_bounce') 

            anim.start(self.ids.locked_img)

    def received_ask_for_password(self, cmd):
        conn.unbind(Command.Types.ASK_FOR_PASSWORD)

        password_popup = DeviceLockedScreen.PasswordPopup(
            title='Device password',
            size_hint=(None, None),
            size=(400, 400),
            auto_dismiss=False,
            on_dismiss_bind_callback=self.received_ask_for_password
        )
        print(password_popup.content)
        password_popup.open()

class PinScreen(Screen):
    class PinTextInput(TextInput):
        def __init__(self, *args, **kwargs):
            super(PinScreen.PinTextInput, self).__init__(*args, **kwargs)
            self._on_backspace_callback = None

        def bind(self, **kwargs):
            if 'on_backspace' in kwargs:
                self._on_backspace_callback = kwargs['on_backspace']
            else:
                super().bind(**kwargs)

        def do_backspace(self, from_undo=False, mode='bkspc'):
            if len(self.text) >= 1 or self._on_backspace_callback is None:
                return super().do_backspace(from_undo, mode)
            else:
                self._on_backspace_callback(self)

            return True



    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        conn.bind(on_receive=self.received_pin, type=Command.Types.ASK_FOR_PIN)
        self.text_inputs = [
            self.ids.pin_text_input_0,
            self.ids.pin_text_input_1,
            self.ids.pin_text_input_2,
            self.ids.pin_text_input_3,
        ]

        for text_input in self.text_inputs:
            text_input.bind(
                text=self.change_to_next_char
            )
            text_input.bind(
                on_backspace=self.change_to_prev_char
            )
        
    def received_pin(self, reply):
        if reply['reply_code'] == Command.Codes.SUCCESS:
            sm.add_widget(MainScreen(name='main_screen'))
            sm.current = 'main_screen'

    def change_to_next_char(self, instance, value):
        instance.focus = False
        idx = self.text_inputs.index(instance)

        if idx + 1 < len(self.text_inputs):
            self.text_inputs[idx + 1].focus = True
        else:
            pin = ''.join([text_input.text[0] for text_input in self.text_inputs])
            print(pin)
            conn.send_pin(pin)

    def change_to_prev_char(self, instance):
        instance.focus = False
        idx = self.text_inputs.index(instance)

        if idx > 0:
            self.text_inputs[idx - 1].text = ''
            self.text_inputs[idx - 1].focus = True

class BaseShadowWidget(Widget):
    pass

class ElevatedGridLayout(RectangularElevationBehavior, BaseShadowWidget, MDGridLayout):
    pass

                   
class CredentialField(MDTextField):
    def __init__(self, **kwargs):
        self.encrypted = kwargs.pop('encrypted', False)
        super().__init__(**kwargs)
        self.font_name = './res/fonts/NotoSans-Regular.ttf'
        self.password_mask = "●"
        self.line_color_normal = App.get_running_app().theme_cls.accent_color
        # self.hint_text = kwargs.get('hint_text', 'Field')
        self.disabled = True

        if self.encrypted:
            self.text = self.hint_text or "_default_"
            self.password = True
            self.icon_right = 'eye-off'


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
                        self.icon_right = 'eye'
                        self.password = False

                    else:
                        self.icon_right = 'eye-off'
                        self.password = True

                    # try to adjust cursor position
                    cursor = self.cursor
                    self.cursor = (0,0)
                    Clock.schedule_once(functools.partial(self.set_cursor, cursor))
        return super(CredentialField, self).on_touch_down(touch)

    def set_cursor(self, pos, dt):
        self.cursor = pos

class MainScreen(Screen):
    class Separator(Widget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.size_hint_y = None
            self.height = 2
            with self.canvas:
                Color(rgba=[0.62, 0.18, 0.18, 1])
                self.rect = Rectangle(pos=(0, self.center_y), size=(self.width, 2))
                
            self.bind(pos=self.update_rect, size=self.update_rect)

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # conn.bind(on_receive=self.received_load_credentials, type=Command.Types.LIST_CREDENTIALS)

        # conn.send_list_credentials()
        # self.add_credential("github", "https://github.com")
        self.add_credential("stackoverflow", "")

    def received_load_credentials(self, reply):
        print(reply['options'])

    @functools.lru_cache()
    def get_credential_icon(self, url):
        try:
            return list(filter(lambda x: x.format in ['png', 'ico'], favicon.get(url)))[0].url
        except:
            return'./res/img/locked.png'

    def add_credential(self, name=None, url=None):
        icon_url = self.get_credential_icon(None)

        entry = TwoLineAvatarListItem( text= "Google",
                            secondary_text="google.com")

        entry.add_widget(IconLeftWidget(icon="google"))
        entry.bind(on_release=self.show_credential_details)

        self.ids.credential_list.add_widget(MDSeparator())
        self.ids.credential_list.add_widget(entry)


    @functools.lru_cache()
    def ask_for_credential_details(self, name):
        return {'name': name, 'url': 'https://github.com', 'user': None, 'password': None}

    def show_credential_details(self, instance):
        details = self.ask_for_credential_details(instance.text)
        self.ids.details_layout.clear_widgets()
        for k,v in details.items():
            self.ids.details_layout.add_widget(
                CredentialField(hint_text=k, text=v or '', encrypted=(v is None))
            )
        




class PiPassApp(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.theme_cls.primary_palette = 'Gray'
        self.theme_cls.accent_palette = 'Red'
        self.theme_cls.theme_style = 'Dark'

        sm.add_widget(MainScreen(name='main_screen'))

        return sm

    def on_request_close(self, *args):
        print('Exiting app..')
        print(conn)
        conn.close()
        print('conn_open = {}'.format(conn.is_open()))
        self.textpopup(title='Exit', text='Are you sure?')
        
        return True

    def textpopup(self, title='', text=''):
        """Open the pop-up with the name.
 
        :param title: title of the pop-up to open
        :type title: str
        :param text: main text of the pop-up to open
        :type text: str
        :rtype: None
        """
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        mybutton = Button(text='OK', size_hint=(1, 0.25))
        box.add_widget(mybutton)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        mybutton.bind(on_release=self.stop)
        popup.open()

if __name__ == "__main__":
    try:
        PiPassApp().run()
    except Exception as e:
        print(repr(e))
        print(''.join(traceback.format_exception(None, e, e.__traceback__)))
        if conn:
            conn.close()