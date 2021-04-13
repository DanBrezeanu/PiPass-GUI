from kivy.clock import Clock
from kivymd.app import MDApp as App
from kivymd.uix.screen import MDScreen

from connection import search_for_device, Connection, Command
from screens.pin_screen import PinScreen
from screens.device_locked_screen import DeviceLockedScreen

class DeviceLoadingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.device_status = False
        Clock.schedule_interval(lambda *args: search_for_device(self.get_device_status), 1)
    
    def get_device_status(self, status):
        if self.device_status == False and status == True:
            if self.app.connection is None:
                self.app.connection = Connection()
                self.app.connection.bind(self.received_hello, Command.Types.APP_HELLO)
                self.app.connection.send_app_hello()
        elif self.device_status == True and status == False:
            self.app.screen_manager.clear_widgets()
            self.app.screen_manager.add_widget(DeviceLoadingScreen(name='device_loading'))
            self.app.screen_manager.current = 'device_loading'

        self.device_status = status

    def received_hello(self, reply):
        self.app.connection.unbind(Command.Types.APP_HELLO)

        if reply['options'] == '1':
            self.app.screen_manager.add_widget(PinScreen(name='pin_screen'))
            self.app.screen_manager.current = 'pin_screen'
        else:
            print("DEVICE LOCKED")
            self.app.screen_manager.add_widget(DeviceLockedScreen(name='locked_screen'))
            self.app.screen_manager.current = 'locked_screen'