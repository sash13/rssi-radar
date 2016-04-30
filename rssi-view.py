#!/usr/bin/env python
from __future__ import print_function
from ble_data import *
import sys

timeout = 1

def clear():
  """Clear screen, return cursor to top left"""
  sys.stdout.write('\033[2J')
  sys.stdout.write('\033[H')
  sys.stdout.flush()
  
def process(fetch):
  devices = fetch.fetch()
  clear()
  for device in devices:
    print(device, devices[device])
  sys.stdout.flush()

fetch = BleDataFetch(timeout = timeout)
try:
  while True:
    process(fetch)      
except KeyboardInterrupt:
  fetch.stop()
  

