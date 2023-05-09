from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
from datetime import datetime, timezone
import serial, time, os, influxdb_client


bucket = "Pluvio2_S"
org = "NTUCE"
client = InfluxDBClient(url="http://localhost:8086", token=os.environ["INFLUXDB_TOKEN"], org=org)
pluvioS_port = '/dev/ttyUSB2'

pluvioS = serial.Serial(pluvioS_port, 
                        baudrate = 9600, 
                        parity = serial.PARITY_NONE, 
                        stopbits = serial.STOPBITS_ONE, 
                        bytesize = serial.EIGHTBITS, 
                        interCharTimeout=1)
pluvioS.xonxoff = False
pluvioS.rtscts = False
pluvioS.dsrdtr = False

def get_data(serialport: serial.Serial):
    serialport.write('M \r\n'.encode('ascii'))      ## The space between \r\n is saperator.
    return [float(i) for i in pluvioS.readline().decode('ascii').split()]

def wait_until_next_minute(timestamp: datetime):
    second_now = timestamp.second + timestamp.microsecond/1000000
    time_to_wait = 60 - second_now
    time.sleep(time_to_wait)
    
def package_response(rsp: list, timestamp: datetime):
    intensity = {
        "measurement": "intensity",
        "fields":{
            "intensity": rsp[0]
        },
        "time": timestamp.isoformat()
    }
    accu = {
        "measurement": "accu",
        "fields":{
            "Accu RT-NRT": rsp[1],
            "Accu NRT": rsp[2], 
            "Accu total NRT" : rsp[3]
        },
        "time": timestamp.isoformat()
    }
    bucket = {
        "measurement": "bucket",
        "fields":{
            "Bucket RT": rsp[4],
            "Bueket NRT": rsp[5]
        },
        "time": timestamp.isoformat()
    }
    machine = {
        "measurement": "machine",
        "fields":{
            "Temperature load cell": rsp[6],
            "Heater status": rsp[7],
            "Status": rsp[8]
        },
        "time": timestamp.isoformat()
    }
    points = [
        Point.from_dict(intensity),
        Point.from_dict(accu),
        Point.from_dict(bucket),
        Point.from_dict(machine)
    ]
    return points

if pluvioS.isOpen():
    pluvioS.flushInput() #flush input buffer
    pluvioS.flushOutput() #flush output buffer
    print('Open: ' + pluvioS.portstr)

    while True:
        try:
            # Wait until next 1 minute time
            timestamp = datetime.now(timezone.utc).astimezone()
            wait_until_next_minute(timestamp)
            timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
         
            response = get_data(pluvioS)
        
            points = package_response(response, timestamp)
            client.write_api(write_options = SYNCHRONOUS).write(bucket=bucket, org=org, record=points)
	    
        except Exception as e1:
            print ("Communicating Error " + str(e1))
            pass
    pluvioS.close()

else:
    print ("open serial port error")