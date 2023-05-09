import os, time
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from parsivel2 import Parsivel2, table

client = InfluxDBClient(url="http://localhost:8086", token=os.environ["INFLUXDB_TOKEN"], org="NTUCE")
port_name = "/dev/ttyUSB3"

def package_wether_parameter(poll: list, timestamp: datetime):
    wether_parameters = {
        "measurement": "weather_parameters",
        "fields": {
            table[1][0]: table[1][1](poll[1]), 
            table[2][0]: table[2][1](poll[2]),
            table[3][0]: table[3][1](poll[3]),
            table[5][0]: table[5][1](poll[5]),
            table[7][0]: table[7][1](poll[7]), 
            table[8][0]: table[8][1](poll[8]), 
            table[34][0]: table[34][1](poll[34])
        },
        "time": timestamp.isoformat()
    }
    return Point.from_dict(wether_parameters)

def package_machine_status(poll: list, timestamp: datetime):
    machine_status = {
        "measurement": "machine status",
        "fields": {
            table[10][0]: table[10][1](poll[10]), 
            table[12][0]: table[12][1](poll[12]),
            table[16][0]: table[16][1](poll[16]), 
            table[17][0]: table[17][1](poll[17]), 
            table[18][0]: table[18][1](poll[18]), 
            table[26][0]: table[26][1](poll[26]),
            table[27][0]: table[27][1](poll[27]), 
            table[28][0]: table[28][1](poll[28]), 
        },
        "time": timestamp.isoformat()
    }
    return Point.from_dict(machine_status)

## What is this?
def package_raw_volume(poll: list, timestamp: datetime):
    raw_volume = []

    for i, volume in enumerate(poll[90].split(";")[:-1]):
        if(float(volume) == -9.999): 
            continue
        raw_volume.append(Point.from_dict({
            "measurement": "raw_volume",
            "tags": {"Diameter Class": i+1},
            "fields": {'Volume eq. diameter': table[90][1](volume)},
            "time": timestamp.isoformat()
        }))
        
    return raw_volume

def package_raw_speed(poll: list, timestamp: datetime):
    raw_speed = []
        
    for i, speed in enumerate(poll[91].split(";")[:-1]):
        if(float(speed) == 0): 
            continue
        raw_speed.append(Point.from_dict({
            "measurement": "raw_speed",
            "tags": {"Diameter Class": i+1},
            "fields": {'Average speed': table[91][1](speed)},
            "time": timestamp.isoformat()
        }))
        
    return raw_speed

def package_raw_particle(poll: list, timestamp: datetime):
    raw = []
    data = poll[93].split(";")[:-1]
    for i in range(len(data)):
        if(int(data[i]) == 0): continue
        raw.append(Point.from_dict({
            "measurement": "raw_particle",
            "tags": {
                "Speed Class": i//32 + 1,
                "Diameter Class": i%32 + 1
            },
            "fields": {
                "Number": table[93][1](data[i])
            },
            "time": timestamp.isoformat()
        }))
    return raw

def wait_until_next_tensecond(timestamp: datetime):
    second_now = timestamp.second + timestamp.microsecond/1000000 # Or .now() for local time
    time_to_wait = 10 - second_now%10
    time.sleep(time_to_wait)

with Parsivel2(port_name) as pv2:
    while True:
        # Wait until next 10 second time
        timestamp = datetime.now(timezone.utc).astimezone()
        wait_until_next_tensecond(timestamp)
        timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
        
        new_poll = pv2.update()

        wether_data = package_wether_parameter(new_poll, timestamp)
        machine_data = package_machine_status(new_poll, timestamp)
        raw_volume_data = package_raw_volume(new_poll, timestamp)
        raw_speed_data = package_raw_speed(new_poll, timestamp)
        raw_particle = package_raw_particle(new_poll, timestamp)

        client.write_api(write_options = SYNCHRONOUS).write(bucket="OTT_Parsivel_2",org="NTUCE",record=wether_data)
        client.write_api(write_options = SYNCHRONOUS).write(bucket="OTT_Parsivel_2",org="NTUCE",record=machine_data)
        client.write_api(write_options = SYNCHRONOUS).write(bucket="OTT_Parsivel_2",org="NTUCE",record=raw_volume_data)
        client.write_api(write_options = SYNCHRONOUS).write(bucket="OTT_Parsivel_2",org="NTUCE",record=raw_speed_data)
        client.write_api(write_options = SYNCHRONOUS).write(bucket="OTT_Parsivel_2",org="NTUCE",record=raw_particle)