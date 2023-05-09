import os, time
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from TB4series2 import TBRG, re_TBRG_closure, re_TBRG_daily_summary
import re

client = InfluxDBClient(url="http://localhost:8086", token=os.environ["INFLUXDB_TOKEN"], org="NTUCE")
tbrg_port = '/dev/ttyUSB0'

##The operation of TBRG is really restricted
##We can only litening to the port and record the time of each closure


def package_closure(timestamp: datetime):
    closure = {
        "measurement": "closure",
        "fields": {
            "mm" : 0.2
        },
        "time": timestamp.isoformat()
    }
    return Point.from_dict(closure)

def package_daily_summary(closure_count: int, timestamp: datetime):
    summary = {
        "measurement": "daily_summary",
        "fields": {
            "closure_count": closure_count
        },
        "time": timestamp.isoformat()
    }
    return Point.from_dict(summary)



with TBRG(port = tbrg_port) as tb4:
    while True:
        data = str(tb4.read_respond().decode())

        if(re.match(re_TBRG_closure, data)):    ## HH:MM:SS
            timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
            point_package = package_closure(timestamp)            
            client.write_api(write_options=SYNCHRONOUS).write(bucket="TBRG", org="NTUCE", record=point_package)
        elif(re.match(re_TBRG_daily_summary, data)):  ## HH:MM:SS dd/mm/yy ccc\r\n
            timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
            point_package = package_daily_summary(int(data[18:-2]), timestamp)
            client.write_api(write_options=SYNCHRONOUS).write(bucket="TBRG", org="NTUCE", record=point_package)
        elif(len(data) != 0):
            print(f'unknown: {data.encode()}')

        time.sleep(0.5)