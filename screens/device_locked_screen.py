from kivymd.app import MDApp as App
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDTextButton
from kivy.animation import Animation

from connection import Command
from screens.pin_screen import PinScreen

class DeviceLockedScreen(MDScreen):
    class PasswordPopup(Popup):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self._on_dismiss_bind_callback = kwargs.get('on_dismiss_bind_callback', None)
            content = MDBoxLayout(orientation='vertical', spacing=5,padding=(30,30,30,30))

            content.add_widget(
                MDLabel(
                    text='Enter the password to unlock the device',
                    pos_hint = {'center_x': .5, 'center_y': .5},
                    halign='center'
                )
            )

            text_input = MDTextField(
                multiline=False,
                password=True,
                size_hint=(1, 0.2),
                background_color=(0.11, 0.11, 0.11, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1),
            )
            content.add_widget(text_input)

            content.add_widget(
                MDTextButton(
                    text='OK',
                    size_hint=(1, 0.3),
                    on_release=lambda *args: conn.send_password(text_input.text)
                )
            )

            content.add_widget(
                MDTextButton(
                    text='Cancel',
                    size_hint=(1, 0.3),
                    on_release=self.dismiss
                )
            )

            self.content = content
         

        def dismiss(self, *args, **kwargs):
            super().dismiss(*args, **kwargs)
            self.app.connection.bind(
                on_receive=self._on_dismiss_bind_callback,
                type=Command.Types.ASK_FOR_PASSWORD,
            )

            

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = App.get_running_app()
        print(self.app.connection)
        self.app.connection.bind(on_receive=self.received_hello, type=Command.Types.APP_HELLO)
        self.app.connection.bind(on_receive=self.received_ask_for_password, type=Command.Types.ASK_FOR_PASSWORD)
        self.ids.try_again_button.bind(
            on_press=lambda *args:  self.app.connection.send_app_hello()
        )
        
    def received_hello(self, reply):
        if reply['options'] == '1':
            self.app.connection.unbind(Command.Types.APP_HELLO)
            self.app.screen_manager.add_widget(PinScreen(name='pin_screen'))
            self.app.screen_manager.current = 'pin_screen'
        else:
            initial_pos = self.ids.locked_img.x
            initial_pos_y = self.ids.locked_img.y
            # TODO: make this work
            anim = Animation(pos=(initial_pos + 50, initial_pos_y+ 50), duration=.5, t='out_bounce') + \
                   Animation(pos=(initial_pos + 50, initial_pos_y+ 50), duration=.1, t='out_bounce') 

            anim.start(self.ids.locked_img)

    def received_ask_for_password(self, cmd):
        self.app.connection.unbind(Command.Types.ASK_FOR_PASSWORD)

        password_popup = DeviceLockedScreen.PasswordPopup(
            title='Device password',
            size_hint=(None, None),
            size=(400, 400),
            auto_dismiss=False,
            on_dismiss_bind_callback=self.received_ask_for_password
        )
        print(password_popup.content)
        password_popup.open()
