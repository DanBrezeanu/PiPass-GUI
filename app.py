from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

from connection import search_for_device, Connection, Command

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
        Clock.schedule_interval(lambda *args: search_for_device(self.get_device_status), 1)
        self.device_status = False
    
    def get_device_status(self, status):
        global conn

        if self.device_status == False and status == True:
            conn = Connection()

            conn.bind(self.received_hello, Command.Types.APP_HELLO)
            conn.send_app_hello()

        elif self.device_status == True and status == False:
            sm.clear_widgets()
            sm.add_widget(DeviceLoadingScreen(name='device_loading'))
            sm.current = 'device_loading'

        self.device_status = status

    def received_hello(self, reply):
        if c.body['options'] == '1':
            sm.add_widget(PinScreen(name='pin_screen'))
            sm.current = 'pin_screen'
        else:
            print("DEVICE LOCKED")
            sm.add_widget(PinScreen(name='pin_screen'))
            sm.current = 'pin_screen'
            
class PinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.pin_text_input.bind(
            on_text_validate=lambda *args: conn.send_pin(self.ids.pin_text_input.text)
        )
        

class PiPassApp(App):
    def build(self):
        sm.add_widget(DeviceLoadingScreen(name='device_loading'))

        return sm

    def on_request_close(self, *args, **kwargs):
        print('Exiting app..')
        conn.close()
        return True

if __name__ == "__main__":
    PiPassApp().run()