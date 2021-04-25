from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from screens.main_screen.components.fields import PasswordTextField, MultipleIconTextField
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.core.clipboard import Clipboard

class CredentialInformationBody(MDBoxLayout):
    pass


class AddCredentialBody(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected = None

    def change_to_password_form(self, *args):
        self.ids.form_layout.clear_widgets()
        self._fields = []

        name_field = MultipleIconTextField(hint_text="Name", size_hint_y=None)
        self.ids.form_layout.add_widget(name_field)
        self._fields.append(name_field)

        password_field = MultipleIconTextField(
            hint_text="Password",
            size_hint_y=None,
            is_password=True,
            icons=['content-copy'],
        )
        password_field.bind_action(on_content_copy=lambda *args: Clipboard.copy(password_field.text))
        self.ids.form_layout.add_widget(password_field)
        self._fields.append(password_field)

        url_field = MultipleIconTextField(hint_text="URL", size_hint_y=None)
        self.ids.form_layout.add_widget(url_field)
        self._fields.append(url_field)

        self.selected = 'password'

    def change_to_card_form(self, *args):
        self.selected = 'card'

    def change_to_other_form(self, *args):
        self.selected = 'other'

    def get_form_information(self):
        return {
            'type': self.selected,
            'fields': [
                {
                    'name': field.hint_text.lower(),
                    'data': field.text,
                    'encrypted': field.encrypted,
                }
                for field in self._fields
            ]
        }