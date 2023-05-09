import time
import serial
import re

re_TBRG_closure = '^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)\r\n$'
re_TBRG_daily_summary = '^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)\s[0-3]?[0-9]\/[0-3]?[0-9]\/(?:[0-9]{2})?[0-9]{2}\s[0-9]{1,4}\r\n$'

class TBRG:
    def __init__(self, port="COM1", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
    
    def __enter__(self):
        return self.open()
    
    def __exit__(self):
        self.close()
    
    def open(self):
        self.serial = serial.Serial(self.port, baudrate = self.baudrate, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, interCharTimeout=1)
        self.serial.xnoxoff = False
        self.serial.rtscts = False
        self.serial.dsrdtr = False
        return self
    
    def close(self):
        self.serial.close()
        
    def send_request(self, command: str):
        command += "\r\n"
        command = command.encode("ascii")
        self.serial.write(command)
        return

    def read_respond(self, timeout = 10) -> str:
        timeout_count = 0
        data = b''
        while True:
            if self.serial.inWaiting() > 0:
                new_data = self.serial.read(1)
                data = data + new_data
                timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= 10 * timeout:
                    break
                time.sleep(0.01)
        return data
            

    