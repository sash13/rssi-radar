#!/usr/bin/env python
### BLE radar
# This sketch for searching Bluetooth 4.0 Smart BLE whatever
# For propertly work you must install bluepy https://github.com/IanHarvey/bluepy
# For testing type in console:
#   $ sudo hciconfig hci0 up
#   $ sudo python radar.py
# And find or power on you BLE tags

import Tkinter as tk
from ble_data import *
import math
import random

WIDTH = 400
HEIGHT = 400
TIMEOUT_COUNT = 20

#thx to `mgold` from sof
def _create_circle(self, x, y, r, **kwargs):
  return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)  
tk.Canvas.create_circle = _create_circle

class Application(tk.Frame):
  def __init__(self, master=None, data=None):
    tk.Frame.__init__(self, master, width=WIDTH, height=HEIGHT)
    master.protocol("WM_DELETE_WINDOW", self.closeWindow)
    self.data = data
    self.master = master

    canvas = self.canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT, bg = "white")
    canvas.pack()

    self.node_center = Point(canvas, (WIDTH/2, HEIGHT/2)) 
    self.node_center.fill = 'black'

    self.nodes = {}
    self.updateNodes()
    self.updateCanvas()

  def closeWindow(self):
    self.data.stop()
    self.master.destroy()

  def updateNodes(self):
    fetch_nodes = self.data.fetch()
    for addr in fetch_nodes:
      if addr not in self.nodes:
        self.nodes[addr] = Point(self.canvas, (WIDTH/2, HEIGHT/2)) 

      self.nodes[addr].go(fetch_nodes[addr])
      self.nodes[addr].count = 0
      self.nodes[addr].setState('blue')

    for addr in self.nodes.keys():
      if addr not in fetch_nodes:
        self.nodes[addr].setState('yellow')
        self.nodes[addr].count += 1
        if self.nodes[addr].count > TIMEOUT_COUNT:
          del self.nodes[addr]

  def updateCanvas(self):
    self.updateNodes()
    self.canvas.delete("all")
    self.node_center.draw()
    for node in self.nodes:
      self.nodes[node].tick()
      self.nodes[node].draw(orbit=True)
    self.master.after(100, self.updateCanvas)

class Point(tk.Frame):
  def __init__(self, parent, c, r=0, center=False):
    self.c = c
    self.r = r
    self.goTo = 0
    self.p = parent
    self.center = center

    self.angle = random.uniform(0, math.pi*2)
    self.fill = "blue"
    self.outline = "#DDD"
    self.size = 10
    self.count = 0

  def go(self, to=0):
    self.goTo = to - self.r

  def setState(self, state = None):
    if state:
      self.fill = state
    else:
      self.fill = "blue"

  def tick(self, tick=0.1):
    self.r += self.goTo*tick

  def draw(self, r=None, orbit=False):
    if r:
      self.r = r
    r = int(self.r)
    if orbit:
      self.p.create_circle(WIDTH/2, HEIGHT/2, r, width=1)
    self.p.create_circle(WIDTH/2 - r*math.cos(self.angle),
                         HEIGHT/2 - r*math.sin(self.angle),
                         self.size, fill=self.fill , outline=self.outline, width=2)

fetch = BleDataFetch()

master = tk.Tk()
master.resizable(width=0, height=0)
app = Application(master, data = fetch)

app.master.title('BLE Viewer')
app.mainloop()