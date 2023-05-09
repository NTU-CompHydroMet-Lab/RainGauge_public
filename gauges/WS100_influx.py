from WS_UMB_EN import WS_UMB
from WS_UMB_EN import channel_discription_unit as allchannels
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point
from datetime import datetime, timezone
import os, time

bucket = "WS100"
org = "NTUCE"
client = InfluxDBClient(url="http://localhost:8086", token=os.environ["INFLUXDB_TOKEN"], org=org)
WS100_port = "/dev/ttyUSB4"
# Store the URL of your InfluxDB instance

def wait_until_next_minute(timestamp: datetime):
    second_now = timestamp.second + timestamp.microsecond/1000000
    time_to_wait = 60 - second_now
    time.sleep(time_to_wait)
    
def get_all_channel_response(umb_device: WS_UMB, channels: list):
    allresponses = {}
    for channel in channels:
            response, status = umb_device.onlineDataQuery(channel[0])
            if status != 0:
                pass
            else:
                allresponses[channel[0]] = response

    return allresponses

def package_data_to_InfluxPoint(response: list, timestamp: datetime):
    ## We need only 
    
    # Machine measurements - 3 fields
    # one of ch133 and ch118 -> ch113
    # ch10000
    # ch11000
    machine = {
        "measurement": "machine",
        "fields":{
            "R2S Heater Temp.": response[113],
            "Supply Voltage": response[10000], 
        },
        "time": timestamp.isoformat()
    }
    
    # Precipitation measurements - 4 fields
    # one of ch600, ch620, ch640 and ch660 -> ch620
    # one of ch605, ch625, ch645 and ch665 -> ch625
    # one of ch800, ch820, ch825, ch840, ch845 and ch860 -> ch820
    # ch700
    # one of ch4100 and ch4105 -> ch4100
    precipitation = {
        "measurement": "precipitation",
        "fields":{
            "Precipitation Quantity-Absolute": response[620],
            "Precipitation Quantity-Differential": response[625], 
            "Precipitation Intensity": response[820],
            "Precipitation Type": response[700],
            "Temperature": response[4100]
        },
        "time": timestamp.isoformat()
    }

    # DSD measurements -18 fields
    # ch11000
    # ch4600, ch4601, ch4602, ch4603, ch4604, ch4620, ch4621, ch4622,
    # ch4623, ch4624, ch4625, ch4626, ch4627, ch4628, ch4629, ch4630, ch4631
    DSD = {
        "measurement": "DSD",
        "fields":{
            "Rain Drop Volume": response[11000],
            "Total Particles": response[4600],
            "Total Drops": response[4601],
            "Drizzle Particles": response[4602],
            "Snow Particles": response[4603],
            "Hail Particles": response[4604],
            "Drop Class 0": response[4620],
            "Drop Class 1": response[4621],
            "Drop Class 2": response[4622],
            "Drop Class 3": response[4623],
            "Drop Class 4": response[4624],
            "Drop Class 5": response[4625],
            "Drop Class 6": response[4626],
            "Drop Class 7": response[4627],
            "Drop Class 8": response[4628],
            "Drop Class 9": response[4629],
            "Drop Class 10": response[4630],
            "Drop Class 11": response[4631]
        },
        "time": timestamp.isoformat()
    }
    
    points = [
        Point.from_dict(machine),
        Point.from_dict(precipitation),
        Point.from_dict(DSD)
    ]
    
    return points

response = {}

with WS_UMB(device = WS100_port) as umb:
    while True:
        #Wait until next 1 minute time
        timestamp = datetime.now(timezone.utc).astimezone()
        wait_until_next_minute(timestamp)
        timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
        
        response = get_all_channel_response(umb, allchannels)
        
        points = package_data_to_InfluxPoint(response, timestamp)
        client.write_api(write_options = SYNCHRONOUS).write(bucket=bucket, org=org, record=points)


        
        
