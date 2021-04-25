from kivymd.app import MDApp as App
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
import functools
from connection import Command
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
import random
import string

class PasswordTextField(MDTextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon_right_color = (1, 1, 1, 1)
        self.app = App.get_running_app()
        self.line_color_normal = App.get_running_app().theme_cls.accent_color
        self.password_mask = "\u2022"
        self.font_name_hint_text = './res/fonts/NotoSans-Regular.ttf'

        if self.password:
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
                        self.reveal()
                    else:
                        self.hide()
                        
                    # try to adjust cursor position
                    cursor = self.cursor
                    self.cursor = (0,0)
                    Clock.schedule_once(functools.partial(self.set_cursor, cursor))
        return super().on_touch_down(touch)

    def reveal(self):
        self.password = False
        self.icon_right = 'eye'

    def hide(self):
        self.password = True
        self.icon_right = 'eye-off'

    def set_cursor(self, pos, dt):
        self.cursor = pos


class MultipleIconTextField(MDBoxLayout):
    def __init__(self, **kwargs):
        self.encrypted = kwargs.pop('encrypted', False)
        icons = kwargs.pop('icons', [])

        self._is_password = kwargs.pop('is_password', False)
        self.encrypted = self._is_password or self.encrypted

        self._text_field = PasswordTextField(
            text=kwargs.pop('text', ''),
            password=self.encrypted,
        )
        self._text_field.hint_text = kwargs.pop('hint_text', '')

        self._icons = icons.copy()
        self._callbacks = {k: v for k, v in kwargs.items() if k.startswith('on_')}
        for k in self._callbacks:
            kwargs.pop(k)

        self._icon_buttons = []
        if self._is_password:
            self._icon_buttons.append(MDIconButton(icon='refresh', on_release=self.generate_password))
        elif self.encrypted:
            self._icon_buttons.append(MDIconButton(icon='lock-outline', on_release=self.on_change_encryption_status))
        else:
            self._icon_buttons.append(MDIconButton(icon='lock-open-variant-outline', on_release=self.on_change_encryption_status))

        for icon in self._icons:
            icon_callback_name = f"on_{icon.replace('-', '_')}"

            icon_button = MDIconButton(icon=icon)
            if self._callbacks.get(icon_callback_name, None):
                icon_button.bind(on_release=self._callbacks[icon_callback_name])
            self._icon_buttons.append(icon_button)
            
        kwargs['orientation'] = 'horizontal'
        super().__init__(**kwargs)

        self.add_widget(self._text_field)
        
        for icon_button in self._icon_buttons:
            self.add_widget(icon_button)

    @property
    def text(self):
        return self._text_field.text

    @property
    def hint_text(self):
        return self._text_field.hint_text

    def bind_action(self, **kwargs):
        callback_name = [k for k in kwargs.keys() if k.startswith('on_')].pop()
        self._callbacks[callback_name] = kwargs[callback_name]

        for icon_button in self._icon_buttons:
            if icon_button.icon == callback_name[3:].replace('_', '-'):
                icon_button.unbind()
                print(f'bound to {icon_button.icon}')
                icon_button.bind(on_release=self._callbacks.get(callback_name, None))
                break

    def generate_password(self, *args):
        self._text_field.text = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        self._text_field.focus = True

    def on_change_encryption_status(self, *args):
        self.encrypted = not self.encrypted

        for icon_button in self._icon_buttons:
            if icon_button.icon.startswith('lock-'):
                icon_button.icon = 'lock-outline' if self.encrypted else 'lock-open-variant-outline'
                break




class CredentialField(PasswordTextField):
    def __init__(self, **kwargs):
        self.encrypted = kwargs.pop('encrypted', False)
        if self.encrypted:
            kwargs['password'] = True

        self.parent_credential = kwargs.pop('parent_credential', None)
        super().__init__(**kwargs)
        self.disabled = True

        if self.encrypted:
            self.text = self.hint_text or "_default_"
    
    def reveal(self):
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
    
    def hide(self):
        self.text = self.hint_text if self.hint_text else '_default_'
        self.password = True
        self.icon_right = 'eye-off'

    def reveal_credential_info(self, reply):
        print('in reveal credneital')
        self.app.connection.unbind(Command.Types.ENCRYPTED_FIELD_VALUE)
        self.text = reply['options']
        self.icon_right = 'eye'
        self.password = False