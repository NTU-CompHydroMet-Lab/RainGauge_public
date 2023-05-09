import time
import serial

class Parsivel2:
    def __init__(self, port = "COM1", baudrate = 19200):
        self.port = port
        self.baudrate = baudrate
        self.poll = [""]*100

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

    def update(self):
        ## This function take a full poll and update everything just like ASDO.
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        buffer = self.PollAll().split(b'\r\n')
        for line in buffer[1:-1]:       ## Pass TYP OP4A at index 0 and ETX at last element
            line = line.decode()
            self.poll[int(str(line[0:2]))] = str(line[3:])
        return self.poll
    
    def FactorySetting(self):
        ## CS/F/1
        pass
    def SamplingInterval(self, interval: int):
        ## CS/I/<parameter>
        ## Setup auto polling 
        ## There's no \r\n at the end of polling.
        pass
    def Poll(self) -> str:
        ## CS/P
        ## This command disable interval-controlled telegram (CS/I/<parameter>)
        ## Consider re-enable the interval-controlled telegram
        ## There's no \r\n at the end of polling.
        pass
    def PollAll(self) -> str:
        ## CS/PA
        ## This command disable interval-controlled telegram (CS/I/<parameter>)r
        self.send_request("CS/PA")        
        return self.read_respond(10)

    def PollRepeat(self) -> str:
        ## CS/R
        ## This command DO NOT disable interval-controled telegram (CS/I/<parameter>)
        pass
    def PollFromNumber(self, number: int):
        ## CS/R/<number>
        ## This command DO NOT disable interval-controled telegram (CS/I/<parameter>)
        pass
    def BautRateSet(self, bautrate: int):
        ## CS/C/R/<parameter>
        ## May cause loss of conectivity
        ## Limited to standard baudrate
        pass
    def Baudrate(self) -> int:
        ## CS/C/R
        ## Return current baudrate
        pass
    def BussModeToggle(self) -> str:
        ## CS/C/B/<parameter>
        ## <parameter> can only be 0 or 1. So this function is a toggle.
        ## This command may return address
        pass
    def BussAddress(self, address: int):
        ## CS/C/A/<parameter>
        ## This may cause connectivity
        ## <parameter> is 0~9 and factory setting is 0
        pass
    def DeployTimeSet(self, hour: int, min: int, sec: int) -> str:
        ## CS/T/HH:MM:SS
        ## Set the time when Parsivel2 got deployed.
        ## This command is a little blur. Make sure we can set our own time.
        ## This command broke.
        pass
    def DeployDateSet(self, DD: int, MM: int, YYYY: int) -> str:
        ## CS/D/DD.MM.YYYY
        ## Set the date when Parsivel2 got deployed.
        ## This command broke.
        pass
    def StationNameSet(self, name: str) -> str:
        ## CS/K/<name>
        ## Name should be less than 10 character
        pass
    def StationIdSet(self, id: int) -> int:
        ## CS/J/<ID>
        ## ID is four digit
        pass
    def TelegramMode(self, toggle: bool) -> int:
        ## CS/M/M/<parameter>
        ## <parameter> is 0(OTT telegram) or 1(User telegram)
        pass
    def TelegramFormat(self, numbers: list[int], separator: str) -> str:
        ## CS/M/S/<parameter>
        ## <parameter> is the format mentioned in 11.3
        self.format = ""
        for number in numbers:
            self.format += "%"
            self.format += f'{number:02d}'
            self.format += separator
        self.send_request("CS/M/S/"+self.format)
        self.TelegramFormatGet()
        return self.format

    def TelegramFormatGet(self) -> str:
        ## CS/M/S
        ## Withut parameter it will return the current format
        pass


    def ResetRain(self):
        ## CS/Z/1
        ## Reset the accumulated rain
        pass
    def Config(self) -> str:
        ## CS/L
        ## Output all configuration
        pass
    def CommandList(self) -> str:
        ## CS/?
        ## Output all commands
        pass
    def HeatingMode(self, mode: int):
        ## CS/H/M/<parameter>
        ## <parameter> is 0, 1 or 3. Which means OFF, Auto and ON.
        pass
    def HeatingThreshold(self, temperature: int):
        ## CS/H/T/<parameter>
        ## <parameter> is between -40 and 40 degree celsius.
        ## 10 default
        pass
    def HeatingMinPower(self, power: int):
        ## CS/H/Q/<parameter>
        ## <parameter> is power of heating in %
        pass
    def HeatingMaxPower(self, power: int):
        ## CS/H/P/<parameter>
        ## <parameter> is power of heating in %
        pass
    def TimeSet(self, DD, MM, YYYY, hh, mm, ss):
        ## CS/U/<parameter>
        ## <parameter> is time and date in format DD.MM.YYYY hh:mm:ss
        pass
    def TimeGet(self):
        ## CS/U
        ## Get current sensor time
        pass
    def Parsievl1Mode(self, bool):
        ## CS/*/D/<parameter>
        ## <parameter> is either 0(Pareivel2 mode) or 1(Parsivel2 mode)
        pass
    def SmearSupression(self, bool):
        ## CS/*/X/<parameter>
        ## <parameter> is either 0(Deactivated) or 1(Activated)
        pass

table = {
    1:["Rain Intensity",float,8,"mm/h"],
    2:["Rain amount accumulated",float,7,"mm"],
    3:["Weather code SYNOP 4680",int,2,""],
    4:["Weather code SYNOP 4677",int,2,""],
    5:["Weather code METER/SPECI 4678",str,5,""],
    6:["Weather code NWS",str,4,""],
    7:["Radar reflectivity",float,6,"dBz"],
    8:["MOR visibility in precipitation",int,5,"m"],
    9:["Sample interval",int,5,"s"],
    10:["Signal amplitude of laser strip",int,5,"1"],
    11:["Number of particles",int,5,"1"],
    12:["Temperature in the sensor housing",int,3,"°C"],
    13:["Sensor serial number",str,6,""],
    14:["Firmware IOP version number",str,6,""],
    15:["Firmware DSP version number",str,6,""],
    16:["Sensor head heating current",float,4,"A"],
    17:["Power supply voltage",float,4,"V"],
    18:["Sensor status",int,1,""],
    19:["Date/time measuring start",str,19,""],
    20:["Sensor time",str,8,""],
    21:["Sensor date",str,10,""],
    22:["Station name",str,10,""],
    23:["Station number",str,4,""],
    24:["Rain amount absolute",float,7,"mm"],
    25:["Error code",str,3,""],
    26:["Temperature PCB",int,3,"°C"],
    27:["Right sensor head temperature",int,3,"°C"],
    28:["Left sensor head temperature",int,3,"°C"],
    30:["Rain intensity max. 30.000 mm/h",float,6,"mm/h"],
    31:["Rain intensity max. 1200.0 mm/h",float,6,"mm/h"],
    32:["Rain amount accumulated",float,7,"mm"],
    33:["Radar reflectivity",float,5,"dBz"],
    34:["Kinetic energy",float,7,"J/(m^2h)"],
    35:["Snow depth intensity",float,7,"mm/h"],
    60:["Number of all particles detected",int,8,"1"],
    61:["List of all particles detected",int,13,"mm;m/s"],
    90:["Field N (d)",float,223,"log(1/m^3mm)"],
    91:["Field v (d)",float,223,"m/s"],
    93:["Raw data N, v",int,4095,"1"]
}

if __name__ == "__main__":
    pass