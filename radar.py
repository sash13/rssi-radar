#! /usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

from ble_data import *
import math
import random

TIMEOUT_COUNT = 20
MUL = 50

def progress_timeout(object):
  x, y, w, h = object.allocation
  object.window.invalidate_rect((0,0,w,h),False)
  return True

# Create a GTK+ widget on which we will draw using Cairo
class Screen(gtk.DrawingArea):

  # Draw in response to an expose-event
  __gsignals__ = { "expose-event": "override" }

  def __init__(self, fetch):
    gtk.DrawingArea.__init__(self)
    self.timer = gobject.timeout_add (100, progress_timeout, self)
    self.data = fetch
    self.nodes = {}
    self.update = gobject.timeout_add (1000, self.updateNodes, self)

  def updateNodes(self, event):
    fetch_nodes = self.data.fetch()
    for addr in fetch_nodes:
      if addr not in self.nodes:
        self.nodes[addr] = Point() 

      self.nodes[addr].setText(rssi2m(fetch_nodes[addr]))
      self.nodes[addr].go(rssi2m(fetch_nodes[addr]))
      self.nodes[addr].count = 0
      self.nodes[addr].setState('blue')
    for addr in self.nodes.keys():
      if addr not in fetch_nodes:
        self.nodes[addr].setState('yellow')
        self.nodes[addr].count += 1
        if self.nodes[addr].count > TIMEOUT_COUNT:
          del self.nodes[addr]
    return True

  # Handle the expose-event by drawing
  def do_expose_event(self, event):
    # Create the cairo context
    cr = self.window.cairo_create()

    # Restrict Cairo to the exposed area; avoid extra work
    cr.rectangle(event.area.x, event.area.y,
        event.area.width, event.area.height)
    cr.clip()
    self.draw(cr, *self.window.get_size())

  def draw(self, cr, width, height):
    # Fill the background with gray
    cr.set_source_rgb(0.5, 1.0, 1.0)
    cr.rectangle(0, 0, width, height)
    cr.fill()

    cr.set_source_rgb(0.0, 0.5, 0.0)
    cr.arc(width / 2.0, height / 2.0, 10, 0, 2 * math.pi)
    cr.fill()

    for node in self.nodes:
      self.nodes[node].tick()
      self.nodes[node].draw(cr, width, height, orbit=True)

class Point():
  def __init__(self, r=0, center=False):
    self.r = r
    self.text = ''
    self.goTo = 0
    self.p = 0
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

  def setText(self, f):
    self.text = str(round(f, 2))

  def tick(self, tick=0.1):
    self.r += self.goTo*tick

  def draw(self, cr, width, height, r=None, orbit=False):
    pi = math.pi
    if r:
      self.r = r
    r = int(self.r*MUL)
    if orbit:
      cr.set_source_rgb(1.0, 0.0, 0.0)
      cr.arc(width / 2.0, height / 2.0, r, 0, 2 * pi)
      cr.stroke()

    x = width/2 - r*math.cos(self.angle)
    y = height/2 - r*math.sin(self.angle)

    cr.set_source_rgb(1.0, 0.0, 0.0)
    cr.arc(x, y, self.size, 0, 2 * pi)
    cr.fill()

    x = x+10 if self.angle < pi/2 or self.angle > (3*pi/2) else x-10
    y = y+10 if self.angle < pi else y-10
    cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(13)
    cr.move_to(x, y)
    cr.show_text(self.text)

# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(Widget):
  fetch = BleDataFetch(timeout = 0.1)
  window = gtk.Window()
  window.set_title('BLE Viewer')
  window.connect("delete-event", gtk.main_quit)
  widget = Widget(fetch)
  widget.show()
  window.add(widget)
  window.present()
  gtk.main()

if __name__ == "__main__":
  run(Screen)
