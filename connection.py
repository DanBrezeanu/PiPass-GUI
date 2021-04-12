import serial.tools.list_ports
from kivy.clock import Clock
from typing import Union
import enum
import json
import struct

def search_for_device(callback=None):
    ports = serial.tools.list_ports.comports()
    connected = any([p.pid == 0x0105 and p.vid == 0x1133 for p in ports])
    
    return callback(connected)

class Serial():
    PACKET_SIZE = 256
    TIMEOUT = 0.1
    _instance = None

    def __init__(self):
        if Serial._instance is not None:
            raise Exception('Singleton')

        ports = [
            p
            for p in serial.tools.list_ports.comports()
            if p.pid == 0x0105 and p.vid == 0x1133
        ]
    
        self._serial = serial.Serial(ports[0].name, timeout=0, write_timeout=0)
        self._serial.flush()
        print("Out waiting: {}".format(self._serial.out_waiting))

        if not self._serial.is_open:
            raise Exception('Could not open serial port {}'.format(port_name))

        Serial._instance = self

    def check_for_input(self, callback):
        if self._serial.in_waiting > 0:
            data = self._serial.read(size=Serial.PACKET_SIZE)

            if data:
                callback(data)

    def write(self, data: Union[str, bytes]):
        self._serial.write(data)
        self._serial.flush()

    def close(self):
        if self._serial:
            self._serial.flushInput()
            self._serial.flushOutput()
            self._serial.close()

    @staticmethod
    def get_instance():
        if not Serial._instance:
            return Serial()

        return Serial._instance

    def is_open(self):
        return self._serial.is_open

class Connection:
    class Decorators:
        @staticmethod
        def send_command(func):
            def wrap(self, *args, **kwargs):
                func(self, *args, **kwargs)

                if self.auth_token is not None:
                    self.command.body['auth_token'] = self.auth_token

                self._send_command()
            return wrap


    _instance = None

    def __init__(self):
        if Connection._instance is not None:
            raise Exception('Singleton Connection')

        self._serial = Serial.get_instance()
        self.command = None
        self._auth_token = None

        self.callbacks = {
            cmd_type: None for cmd_type in Command.Types
        }

        self.read_event = Clock.schedule_interval(
            lambda *args: self._serial.check_for_input(self._read_and_decode_data),
            1
        )

        Connection._instance = self

   

    def bind(self, on_receive=None, type=None):
        self.callbacks[type] = on_receive
        return True

    def unbind(self, type):
        self.callbacks[type] = None
        return True

    def _read_and_decode_data(self, data: bytes):
        c = Command.from_bytes(data)

        print('got {}'.format(c))

        if c.body['type'] == Command.Types.APP_HELLO and c.body['is_reply']:
            if self.callbacks[Command.Types.APP_HELLO]:
                self.callbacks[Command.Types.APP_HELLO](c.body.copy())

        elif c.body['type'] == Command.Types.ASK_FOR_PIN and c.body['is_reply']:
            if c.body['reply_code'] == Command.Codes.SUCCESS and 'auth_token' in c.body:
                self.auth_token = c.body['auth_token']
                self.callbacks[Command.Types.ASK_FOR_PIN](c.body.copy())
        else:
            if self.callbacks[c.body['type']] is not None:
                self.callbacks[c.body['type']](c.body.copy())
    
    @property
    def auth_token(self):
        return self._auth_token

    @auth_token.setter
    def auth_token(self, value):
        self._auth_token = value

    def _send_command(self):
        if self.command is None:
            return

        self._serial.write(self.command.to_bytes())

    @Decorators.send_command
    def send_app_hello(self):
        self.command = Command(Command.Types.APP_HELLO)
    
    @Decorators.send_command
    def send_pin(self, pin: Union[str, bytes]):
        print('have to send pin {}'.format(pin))
        self.command = Command(Command.Types.ASK_FOR_PIN, is_reply=False)
        self.command.body['options'] = pin.deocde('ascii') if isinstance(pin, bytes) else pin

    @Decorators.send_command
    def send_password(self, password: Union[str, bytes]):
        self.command = Command(Command.Types.ASK_FOR_PASSWORD, is_reply=True)
        self.command.body['options'] = password.deocde('ascii') if isinstance(password, bytes) else password

    @Decorators.send_command
    def send_list_credentials(self):
        self.command = Command(Command.Types.LIST_CREDENTIALS)

    def close(self):
        Clock.unschedule(self.read_event)
        self._serial.close()

    def is_open(self):
        return self._serial.is_open()

    @staticmethod
    def get_instance():
        if not Connection._instance:
            return Connection()

        return Connection._instance

class Command:
    HEADER_SIZE = 4

    class Types(enum.Enum):
        NO_COMMAND = 0x00
        APP_HELLO = 0xB0

        LIST_CREDENTIALS        = 0xC0
        DELIVER_CREDENTIALS_HID = 0xC1
        DELIVER_CRED_PASSWD_HID = 0xC2
        DELIVER_CRED_USER_HID   = 0xC3
        DELIVER_CREDENTIALS_ACM = 0xC2
        DELETE_CREDENTIALS      = 0xC3
        STORE_CREDENTIALS       = 0xC4
        EDIT_CREDENTIALS        = 0xC5

        ENROLL_FINGERPRINT = 0xC5
        DELETE_FINGERPRINT = 0xC6
        LIST_FINGERPRINT   = 0xC7

        LOCK_DEVICE        = 0xC8
        WIPE_DEVICE        = 0xC9

        CHANGE_PIN         = 0xCA
        CHANGE_DIP_SWITCH  = 0xCB

        ASK_FOR_PASSWORD   = 0xCC
        ASK_FOR_PIN        = 0xCD

        DEVICE_AUTHENTICATED = 0xCE

    class Codes(enum.Enum):
        SUCCESS = 0x00
        ERROR   = 0x01

    class Senders(enum.Enum):
        NO_SENDER     = 0x00
        SENDER_PIPASS = 0x01
        SENDER_APP    = 0x02
        SENDER_PLUGIN = 0x03

    ENUMS = {"type": Types, "reply_code": Codes, "sender": Senders}

    class EnumEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, enum.Enum):
                return int(obj.value)
            return json.JSONEncoder.default(self, obj)

    @staticmethod
    def parse_enums(d):
        print(d)
        return {k: (v if k not in Command.ENUMS else Command.ENUMS[k](v)) for k, v in d.items()}

    def __init__(
        self,
        type_ = Types.NO_COMMAND,
        reply_code = Codes.SUCCESS,
        is_reply: bool = False
    ):
        self.body = {
            'type': type_,
            'reply_code': reply_code,
            'is_reply': is_reply,
            'sender': Command.Senders.SENDER_APP,
            'options': ''
        }

        self.header = {
            'length': 0,
            'crc': 0,
        }

        self.update_crc()

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Command':
        print(data)
        cmd = cls()

        cmd.header['length'], crc = struct.unpack('<HH', data[:Command.HEADER_SIZE])
        
        cmd.body = data[Command.HEADER_SIZE:cmd.header['length'] + Command.HEADER_SIZE].decode('ascii')
        cmd.body = json.loads(cmd.body, object_hook=Command.parse_enums)
        cmd.update_crc()

        print(cmd.body)

        #TODO: try catch jsonerror
        print (cmd.header['crc'])
        print(crc)
        if crc != cmd.header['crc']:
            #TODO ERROR
            print('CRC DOES NOT MATCH')

        return cmd

    def to_bytes(self) -> bytes:

        print ('to_send: {}'.format(self.body))
        data = b''
        self.update_crc()

        body_as_bytes = json.dumps(self.body, cls=Command.EnumEncoder).encode()
        self.header['length'] = len(body_as_bytes)

        print('len = {}'.format(self.header['length']))

        data += struct.pack('<HH', self.header['length'], self.header['crc'])
        data += body_as_bytes
        data += b'\x00' * (Serial.PACKET_SIZE - len(data))

        print(data)
        
        return data

    @property
    def crc(self):
        self.header['crc']

    def update_crc(self):
        self.header['crc'] = sum(list(bytearray(json.dumps(self.body, cls=Command.EnumEncoder), encoding="ascii"))) % ((1 << 16) - 1)
        if self.body['sender'] == Command.Senders.SENDER_PIPASS:
            self.header['crc'] += 64