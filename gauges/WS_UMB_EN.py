#!/usr/bin/python3

import time
import struct

channel_discription_unit = [
    (100, 'Temperature', '°C'),
    (105, 'Temperature', '°F'),
    (101, 'External Temperature', '°C'),
    (106, 'External Temperature', '°F'),
    (110, 'Dewpoint', '°C'),
    (115, 'Dewpoint', '°F'),
    (111, 'Wind Chill Temperature', '°C'),
    (116, 'Wind Chill Temperature', '°F'),
    (114, 'Wet Bulb Temperature', '°C'),
    (119, 'Wet Bulb Temperature', '°F'),
    (112, 'Wind Heater Temp.', '°C'),
    (113, 'R2S Heater Temp.', '°C'),
    (117, 'Wind Heater Temp.', '°F'),
    (118, 'R2S Heater Temp.', '°F'),
    (200, 'Relative Humidity', '%'),
    (205, 'Absolute Humidity', 'g/m3'),
    (210, 'Mixing Ratio', 'g/kg'),
    (215, 'Specific Enthalpy', 'kJ/kg'),
    (300, 'Abs. Air Pressure', 'hPa'),
    (305, 'Rel. Air Pressure', 'hPa'),
    (310, 'Air Density', 'kg/m3'),
    (400, 'Wind Speed', 'm/s'),
    (405, 'Wind Speed', 'km/h'),
    (410, 'Wind Speed', 'mph'),
    (415, 'Wind Speed', 'kts'),
    (401, 'Wind Speed Fast', 'm/s'),
    (406, 'Wind Speed Fast', 'km/h'),
    (411, 'Wind Speed Fast', 'mph'),
    (416, 'Wind Speed Fast', 'kts'),
    (403, 'Wind Speed Standard Deviation', 'm/s'),
    (413, 'Wind Speed Standard Deviation', 'mph'),
    (500, 'Wind Direction', '°'),
    (501, 'Wind Direction Fast', '°'),
    (502, 'Wind Direction Corr.', '°'),
    (503, 'Wind Direction Standard Deviation', '°'),
    (805, 'Wind Value Quality', '%'),
    (806, 'Wind Value Quality (Fast)', '%'),
    (510, 'Compass Heading', '°'),
    (600, 'Precipitation Quantity-Absolute', 'liters/m2'),
    (620, 'Precipitation Quantity-Absolute', 'mm'),
    (640, 'Precipitation Quantity-Absolute', 'inches'),
    (660, 'Precipitation Quantity-Absolute', 'mil'),
    (605, 'Precipitation Quantity-Differential', 'liters/m2'),
    (625, 'Precipitation Quantity-Differential', 'mm'),
    (645, 'Precipitation Quantity-Differential', 'inches'),
    (665, 'Precipitation Quantity-Differential', 'mil'),
    (700, 'Precipitation Type', '-'),
    (780, 'WMO Synop Code 4680 wawa (Present Weather, automated station)', '-'),
    (781, 'WMO Synop Code 4680 WaWa (Currently not Avalailable)', '-'),
    (785, 'WMO Synop Code 4677 ww (Present Weather, Manned Station)', '-'),
    (786, 'WMO Synop Code 4677 WW (Currently not Available)', '-'),
    (800, 'Precipitation Intensity', 'l/m2/h'),
    (820, 'Precipitation Intensity', 'mm/h'),
    (825, 'Precipitation Intensity', 'mm/min'),
    (840, 'Precipitation Intensity', 'in/h'),
    (845, 'Precipitation Intensity', 'in/min'),
    (860, 'Precipitation Intensity', 'mil/h'),
    (900, 'Global Radiation', 'W/m2'),
    (617, 'Lightning Event (minute)', '-'),
    (10000, 'Supply Voltage V', 'V'),
    (11000, 'Rain Drop Volume μl', 'μl'),
    (4100, 'Temperature', '°C'),
    (4105, 'Temperature', '°F'),
    (4600, 'Precipitation: Total Particles', '-'),
    (4601, 'Precipitation: Total Drops', '-'),
    (4602, 'Precipitation: Drizzle Particles', '-'),
    (4603, 'Precipitation: Snow Particles', '-'),
    (4604, 'Precipitation: Hail Particles', '-'),
    (4620, 'Precipitation: Drop Class 0', '-'),
    (4621, 'Precipitation: Drop Class 1', '-'),
    (4622, 'Precipitation: Drop Class 2', '-'),
    (4623, 'Precipitation: Drop Class 3', '-'),
    (4624, 'Precipitation: Drop Class 4', '-'),
    (4625, 'Precipitation: Drop Class 5', '-'),
    (4626, 'Precipitation: Drop Class 6', '-'),
    (4627, 'Precipitation: Drop Class 7', '-'),
    (4628, 'Precipitation: Drop Class 8', '-'),
    (4629, 'Precipitation: Drop Class 9', '-'),
    (4630, 'Precipitation: Drop Class 10', '-'),
    (4631, 'Precipitation: Drop Class 11', '-')
    ]

class UMBError(BaseException):
    pass

class WS_UMB:
    """
    This is a simple driver for communicating to Weatherstations
    made by the German company Lufft. It implements their UMB-Protocol.
    You just need a USB-to-RS485 dongle and connect it to your PWS 
    according to the wiring diagram you find in the manual.
    Downsides: This class does not replace the UMB-config-tool, because
    its not able to set the config values in your PWS at the moment.
    
    Attributes
    ----------
    device : string
        Serial port. Default is /dev/ttyUSB0
    
    baudrate : integer
        The default baud rate is 19200
        
    Methods
    -------
    onlineDataQuery (channel, receiver_id=1):
        Use this method to request a value from one channel.
        It will return a (value, status) tuple.
        Status number 0 means everything is ok.
        It have more the one PWS on the BUS, use receiver_id to
        distinguish between them.
        
    checkStatus(status):
        You can lookup, what a status number means.
    
    Usage
    -----
    1. In your python-script: 
        from WS_UMB import WS_UMB
        
        with WS_UMB() as umb:
            value, status = umb.onlineDataQuery(SomeChannelNumber)
            if status != 0:
                print(umb.checkStatus(status))
            else:
                print(value)
    
    2. As a standalone program:
        ./WS_UMB.py 100 111 200 300 460 580
    """

    # def __init__(self, device='/dev/ttyUSB0', baudrate=19200):
    def __init__(self, device='COM6', baudrate=19200):
        self.device = device
        self.baudrate = baudrate
    
    def __enter__(self): # throws a SerialException if it cannot connect to device
        import serial
        self.serial = serial.Serial(self.device, baudrate = self.baudrate, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, interCharTimeout=1)
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.serial.close()
    
    def readFromSerial(self, timeout=1):
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
    
    def calc_next_crc_byte(self, crc_buff, nextbyte):
        for i in range (8):
            if( (crc_buff & 0x0001) ^ (nextbyte & 0x01) ):
                x16 = 0x8408;
            else:
                x16 = 0x0000;
            crc_buff = crc_buff >> 1;
            crc_buff ^= x16;
            nextbyte = nextbyte >> 1;
        return(crc_buff);
    
    def calc_crc16(self, data):
        crc = 0xFFFF;
        for byte in data:
            crc = self.calc_next_crc_byte(crc, byte);
        return crc
    
    def send_request(self, receiver_id, command, command_version, payload):
        
        SOH, STX, ETX, EOT= b'\x01', b'\x02', b'\x03', b'\x04'
        VERSION = b'\x10'
        TO = int(receiver_id).to_bytes(1,'little')
        TO_CLASS = b'\x70'
        FROM = int(1).to_bytes(1,'little')
        FROM_CLASS = b'\xF0'
        
        LEN = 2
        for payload_byte in payload:
            LEN += 1
        LEN = int(LEN).to_bytes(1,'little')
        
        COMMAND = int(command).to_bytes(1,'little')
        COMMAND_VERSION = int(command_version).to_bytes(1,'little')
        
        # Assemble transmit-frame
        tx_frame = SOH + VERSION + TO + TO_CLASS + FROM + FROM_CLASS + LEN + STX + COMMAND + COMMAND_VERSION + payload + ETX 
        # calculate checksum for trasmit-frame and concatenate
        tx_frame += self.calc_crc16(tx_frame).to_bytes(2, 'little') + EOT
        
        # Write transmit-frame to serial
        self.serial.write(tx_frame) 
        #print([hex(c) for c in tx_frame])
        
        ### < --- --- > ###
        
        # Read frame from serial
        rx_frame = self.readFromSerial()
        #print([hex(c) for c in rx_frame])
        
        # compare checksum field to calculated checksum
        cs_calculated = self.calc_crc16(rx_frame[:-3]).to_bytes(2, 'little')
        cs_received = rx_frame[-3:-1]
        if (cs_calculated != cs_received):
            raise UMBError("RX-Error! Checksum test failed. Calculated Checksum: " + str(cs_calculated) + "| Received Checksum: " + str(cs_received))
        
        # Check the length of the frame
        length = int.from_bytes(rx_frame[6:7], byteorder='little')
        if (rx_frame[8+length:9+length] != ETX):
            raise UMBError("RX-Error! Length of Payload is not valid. length-field says: " + str(length))
        
        # Check if all frame field are valid
        if (rx_frame[0:1] != SOH):
            raise UMBError("RX-Error! No Start-of-frame Character")
        if (rx_frame[1:2] != VERSION):
            raise UMBError("RX-Error! Wrong Version Number")
        if (rx_frame[2:4] != (FROM + FROM_CLASS)):
            raise UMBError("RX-Error! Wrong Destination ID")
        if (rx_frame[4:6] != (TO + TO_CLASS)):
            raise UMBError("RX-Error! Wrong Source ID")
        if (rx_frame[7:8] != STX):
            raise UMBError("RX-Error! Missing STX field")
        if (rx_frame[8:9] != COMMAND):
            raise UMBError("RX-Error! Wrong Command Number")
        if (rx_frame[9:10] != COMMAND_VERSION):
            raise UMBError("RX-Error! Wrong Command Version Number")
            
        status = int.from_bytes(rx_frame[10:11], byteorder='little')
        type_of_value = int.from_bytes(rx_frame[13:14], byteorder='little')     
        value = 0
        
        if type_of_value == 16:     # UNSIGNED_CHAR
            value = struct.unpack('<B', rx_frame[14:15])[0]
        elif type_of_value == 17:   # SIGNED_CHAR
            value = struct.unpack('<b', rx_frame[14:15])[0]
        elif type_of_value == 18:   # UNSIGNED_SHORT
            value = struct.unpack('<H', rx_frame[14:16])[0]
        elif type_of_value == 19:   # SIGNED_SHORT
            value = struct.unpack('<h', rx_frame[14:16])[0]
        elif type_of_value == 20:   # UNSIGNED_LONG
            value = struct.unpack('<L', rx_frame[14:18])[0]
        elif type_of_value == 21:   # SIGNED_LONG
            value = struct.unpack('<l', rx_frame[14:18])[0]
        elif type_of_value == 22:   # FLOAT
            value = struct.unpack('<f', rx_frame[14:18])[0]
        elif type_of_value == 23:   # DOUBLE
            value = struct.unpack('<d', rx_frame[14:22])[0]
        
        return (value, status)
    
    def checkStatus(self, status):
        if status == 0:
            return ("Status: command successful; no mistake; everything's ok")
        elif status == 16:
            return ("Status: unknown command; is not supported by this device")
        elif status == 17:
            return ("Status: invalid parameters")
        elif status == 18:
            return ("Status: invalid header version")
        elif status == 19:
            return ("Status: invalid version of the command")
        elif status == 20:
            return ("Status: wrong password for command")
        elif status == 32:
            return ("Status: reading error")
        elif status == 33:
            return ("Status: spelling mistake")
        elif status == 34:
            return ("Status: length too big; The maximum permissible length is specified in <maxlength>")
        elif status == 35:
            return ("Status: invalid address / storage location")
        elif status == 36:
            return ("Status: invalid channel")
        elif status == 37:
            return ("Status: command not possible in this mode")
        elif status == 38:
            return ("Status: unknown test / adjustment command")
        elif status == 39:
            return ("Status: calibration error")
        elif status == 40:
            return ("Status: device not ready; e.g. initialization / calibration is running")
        elif status == 41:
            return ("Status: undervoltage")
        elif status == 42:
            return ("Status: hardware failure")
        elif status == 43:
            return ("Status: measurement error")
        elif status == 44:
            return ("Status: device initialization error")
        elif status == 45:
            return ("Status: error in the operating system")
        elif status == 48:
            return ("Status: error in the configuration, default configuration was loaded")
        elif status == 49:
            return ("Status: adjustment error / the adjustment is invalid, measurement not possible")
        elif status == 50:
            return ("Status: CRC error when loading the configuration; Default configuration was loaded")
        elif status == 51:
            return ("Status: CRC error when loading the synchronization data; Measurement not possible")
        elif status == 52:
            return ("Status: adjustment step 1")
        elif status == 53:
            return ("Status: adjustment OK")
        elif status == 54:
            return ("Status: channel deactivated")
    
    def onlineDataQuery (self, channel, receiver_id=1):
        return self.send_request(receiver_id, 35, 16, int(channel).to_bytes(2,'little'))

#dummy class for testing
class WS_UMB_dummy:
    def __init__(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        pass
    def onlineDataQuery (self, channel, receiver_id=1):
        return float(channel), 0
    def checkStatus(self, status):
        return ("Status: unknown command; is not supported by this device")
    def close(self):
        pass

import sys
import json

if __name__ == "__main__":
    with WS_UMB() as umb:
    # with WS_UMB_dummy() as umb:
        mydict = {}  
        for channel in sys.argv[1:]:
            if 100 <= int(channel) <= 29999:
                value, status = umb.onlineDataQuery(channel)
                if status == 0:
                    mydict[channel] = value
                else:
                    sys.stderr.write("On channel " + str(channel) + " got bad " + umb.checkStatus(status) + "\n")
    print (json.dumps(mydict, separators=(',', ': ')))
