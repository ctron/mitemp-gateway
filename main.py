#!/usr/bin/env python3
import sys
from datetime import datetime
import bluetooth._bluetooth as bluez

import time
import os
import json
import math
import requests
from urllib.parse import urljoin, urlencode, quote, quote_plus
from bluetooth_utils import (toggle_device, enable_le_scan,
                             parse_le_advertising_events,
                             disable_le_scan, raw_packet_to_str)

print("Starting up...")

data_schema = os.getenv('DATA_SCHEMA', "vorto:ctron.mitemp.status:1.0.0")

app_id = os.getenv('APP_ID')
device_id = quote(os.environ['DEVICE_ID'])
device_password = os.getenv('DEVICE_PASSWORD')

endpoint = os.getenv('ENDPOINT', "https://http.sandbox.drogue.cloud")
print(endpoint)

denc = quote_plus(device_id)
auth = (f"{denc}@{app_id}", device_password)

path = f"/v1/status"
query = "?" + urlencode(dict(data_schema=data_schema))
url = urljoin(endpoint, path + query)

print(url)

#    status = {
#        "timestamp": math.trunc(time.time() * 1000.0),
#        "rate_send": t[0],
#        "rate_receive": t[1],
#        "bytes_received": fc.bytes_received,
#        "bytes_sent": fc.bytes_sent
#    }
#    print(json.dumps(status))
#    res = requests.post(url, json=status, auth=auth, headers={"Content-Type": "application/json"})

# Use 0 for hci0
dev_id = 0
toggle_device(dev_id, True)

try:
    sock = bluez.hci_open_dev(dev_id)
except:
    print("Cannot open bluetooth device %i" % dev_id)
    raise

# Set filter to "True" to see only one packet per device
enable_le_scan(sock, filter_duplicates=False)

try:
    def le_advertise_packet_handler(mac, adv_type, data, rssi):
        data_str = raw_packet_to_str(data)
        # Check for ATC preamble
        if data_str[6:10] == '1a18':
            temp = int(data_str[22:26], 16) / 10
            hum = int(data_str[26:28], 16)
            batt = int(data_str[28:30], 16)
            print("%s - Device: %s Temp: %sc Humidity: %s%% Batt: %s%%" % \
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mac, temp, hum, batt))

            status = {
                "temp": temp,
                "hum": hum,
                "batt": batt,
            }
            res = requests.post(url, json=status, auth=auth, headers={"Content-Type": "application/json"})
            print("Result: %s" % res)


    # Called on new LE packet
    parse_le_advertising_events(sock,
                                handler=le_advertise_packet_handler,
                                debug=False)
# Scan until Ctrl-C
except KeyboardInterrupt:
    disable_le_scan(sock)