from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from connection import search_for_device, Connection, Command

import traceback

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
        print(status)
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

        if reply['options'] == '1':
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
        Window.bind(on_request_close=self.on_request_close)

        sm.add_widget(DeviceLoadingScreen(name='device_loading'))

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