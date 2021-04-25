from kivymd.app import MDApp as App
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from screens.main_screen.main_screen import MainScreen
from connection import Command

class PinScreen(MDScreen):

    class PinTextInput(MDTextField):
        def __init__(self, *args, **kwargs):
            super(PinScreen.PinTextInput, self).__init__(*args, **kwargs)
            self._on_backspace_callback = None
            self.color_mode: 'custom'
            self.cursor_color = [0, 1, 1, 1]

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
        self.app = App.get_running_app()
        self.app.connection.bind(on_receive=self.received_pin, type=Command.Types.ASK_FOR_PIN)
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
            self.app.screen_manager.add_widget(MainScreen(name='main_screen'))
            self.app.screen_manager.current = 'main_screen'
        else:
            for text_input in self.text_inputs:
                    text_input.text = ''
                    text_input.focus = False
            self.text_inputs[0].focus = True

    def change_to_next_char(self, instance, value):
        instance.focus = False
        idx = self.text_inputs.index(instance)

        if idx + 1 < len(self.text_inputs):
            self.text_inputs[idx + 1].focus = True
        else:
            pin = ''.join([text_input.text[0] for text_input in self.text_inputs])
            print(pin)
            self.app.connection.send_pin(pin)

    def change_to_prev_char(self, instance):
        instance.focus = False
        idx = self.text_inputs.index(instance)

        if idx > 0:
            self.text_inputs[idx - 1].text = ''
            self.text_inputs[idx - 1].focus = True

