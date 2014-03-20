#!/usr/bin/env python
from gi.repository import Gtk

class MyWindow(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, title="Hello World")
    
    self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.add(self.box)

    # Add label describing what to do

    # add ID passphrase box (with options show passphrase, generate new ID)

    # add ListBox which contains children rows one per plugin with checkbox to enable/disable

    # add button to create ID for all checked plugins

    self.button1 = Gtk.Button(label="Hello")
    self.button1.connect("clicked", self.on_button1_clicked)
    self.box.pack_start(self.button1, True, True, 0)

    self.button2 = Gtk.Button(label="Goodbye")
    self.button2.connect("clicked", self.on_button2_clicked)
    self.box.pack_start(self.button2, True, True, 0)

  def on_button1_clicked(self, widget):
    print("Hello")

  def on_button2_clicked(self, widget):
    print("Goodbye")

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
