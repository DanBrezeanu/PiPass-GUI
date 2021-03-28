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
    
        self._serial = serial.Serial(ports[0].name, timeout=Serial.TIMEOUT)

        if not self._serial.is_open:
            raise Exception('Could not open serial port {}'.format(port_name))

        Serial._instance = self

    def check_for_input(self, callback):
        data = self._serial.read(size=Serial.PACKET_SIZE)
        if data:
            callback(data)

    def write(self, data: Union[str, bytes]):
        self._serial.write(data)
        self._serial.flush()

    def close(self):
        if self._serial:
            self._serial.close()

    @staticmethod
    def get_instance():
        if not Serial._instance:
            return Serial()

        return Serial._instance

class Connection:
    _instance = None

    def __init__(self):
        # if Connection._instance is not None:
        #     raise Exception('Singleton Connection')

        self._serial = Serial.get_instance()
        self.command = None
        self.auth_token = None

        self.callbacks = {
            cmd_type: None for cmd_type in Command.Types
        }

        Clock.schedule_interval(
            lambda *args: self._serial.check_for_input(self._read_and_decode_data),
            1
        )

        Connection._instance = self

    def bind(self, on_receive=None, type=None):
        self.callbacks[type] = on_receive

    def unbind(self, type):
        self.callbacks[type] = None

    def _read_and_decode_data(self, data: bytes):
        c = Command.from_bytes(data)

        if c.body['type'] == Command.Types.APP_HELLO and c.body['is_reply']:
            if self.callbacks[Command.Types.APP_HELLO]:
                self.callbacks[Command.Types.APP_HELLO](c.body.copy())

        elif c.body['type'] == Command.Types.ASK_FOR_PIN and c.body['is_reply']:
            print(f"ASK FOR PIN  reply code = {c.body['reply_code']}")
            print(c.body['auth_token'] if 'auth_token' in c.body else 'NO AUTH TOKEN') 

    def send_command(self):
        if self.command is None:
            return

        self._serial.write(self.command.to_bytes())
    
    def send_app_hello(self):
        self.command = Command(Command.Types.APP_HELLO)
        self.send_command()

    def send_pin(self, pin: Union[str, bytes]):
        self.command = Command(Command.Types.ASK_FOR_PIN, is_reply=False)
        self.command.options = pin.encode('utf-8') if isinstance(pin, str) else pin
        self.send_command()


    def send_password(self, password: Union[str, bytes]):
        self.command = Command(Command.Types.ASK_FOR_PASSWORD, is_reply=False)
        self.command.options = password.encode('utf-8') if isinstance(password, str) else password
        self.send_command()

    def close(self):
        self._serial.close()

    @staticmethod
    def get_instance():
        if not Connection._instance:
            return Connection()

        return Connection._instance

class Command:
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
                return str(obj.value)
            return json.JSONEncoder.default(self, obj)

    @staticmethod
    def parse_enums(d):
        key = [enum_key for enum_key in Command.ENUMS if enum_key in d]
        if key:
            return ENUMS[key](d[key])
        else:
            return d

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

        self._crc = 0

        self.update_crc()

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Command':
        cmd = cls()
        cmd.body = data[:-2].decode()
        cmd.body = json.loads(cmd.body, object_hook=Command.parse_enums)
        cmd.update_crc()
        #TODO: try catch jsonerror
        
        crc = struct.unpack('<H', data[-2:])

        if crc != cmd.crc:
            #TODO ERROR
            print('CRC DOES NOT MATCH')

        return cmd

    def to_bytes(self) -> bytes:
        data = json.dumps(self.body, cls=Command.EnumEncoder).encode()
        self.update_crc()
        data += struct.pack('<H', self.crc)
        data += b'\x00' * (Serial.PACKET_SIZE - len(data))
        
        return data

    @property
    def crc(self):
        return self._crc

    def update_crc(self):
        self._crc = sum(list(bytearray(json.dumps(self.body, cls=Command.EnumEncoder), encoding="utf-8"))) % ((1 << 16) - 1)