from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton

class CredentialInformationFooter(MDStackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = 0.6, 1
        self.orientation = 'tb-lr'

        self._edit_button = MDIconButton(size_hint=(0.3, 1), icon='pencil')
        self._edit_button.bind(on_press=self.edit)

        self._delete_button = MDIconButton(size_hint=(0.3, 1), icon='trash-can')
        self._delete_button.bind(on_press=self.delete)

        self.add_widget(self._edit_button)
        self.add_widget(self._delete_button)

    def edit(self, *args):
        pass

    def delete(self, *args):
        pass

class AddCredentialFooter(MDStackLayout):
    def __init__(self, **kwargs):
        self._on_save_callback = kwargs.pop('on_save', None)

        super().__init__(**kwargs)

        self.size_hint = 0.6, 1
        self.orientation = 'tb-lr'

        self._save_button = MDIconButton(size_hint=(0.3, 1), icon='content-save')
        self._save_button.bind(on_press=self.save)

        self._cancel_button = MDRaisedButton(size_hint=(0.3, 1), text='Cancel')
        self._cancel_button.bind(on_press=self.cancel)

        self.add_widget(self._save_button)
        self.add_widget(self._cancel_button)

    def save(self, *args):
        if self._on_save_callback:
            self._on_save_callback()

    def cancel(self, *args):
        pass
