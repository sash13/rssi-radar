#!/usr/bin/env python
from bluepy import btle

#RSSI to meter convertor
def rssi2m(rssi, A=62, n=4.21):
  return pow(10, (-(rssi+A)/(10.0*n)))

class BleDataFetch(object):
  def __init__(self, timeout = 0.1):
    self.timeout = timeout
    self.scan = btle.Scanner()
    self.scan.clear()
    self.scan.start()

  def fetch(self):
    self.scan.clear()
    self.scan.process(self.timeout)
    devices = self.scan.getDevices()
    return {device.addr:device.rssi for device in devices}
      
  def stop(self):
    self.scan.stop()

    

