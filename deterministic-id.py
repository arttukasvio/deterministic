#!/usr/bin/env python
from gi.repository import Gtk
import electrum

class PassphraseWidget(Gtk.Grid):
  def __init__(self):
    Gtk.Grid.__init__(self)

    # passphrase field
    self.passphrase = Gtk.Entry(visibility=True, expand=True)
    self.passphrase.connect('cut-clipboard', self.validate)
    self.passphrase.connect('delete-from-cursor', self.validate)
    self.passphrase.connect('insert-at-cursor', self.validate)
    self.passphrase.connect('paste-clipboard', self.validate)
    self.passphrase.get_buffer().connect('deleted-text', self.validate)
    self.passphrase.get_buffer().connect('inserted-text', self.validate)
    self.attach(self.passphrase, 0, 0, 1, 1)

    # show/hide passphrase
    hbox = Gtk.Box()
    self.showhide_l = Gtk.Label('Show passphrase:')
    self.showhide_w = Gtk.Switch(active=True)
    self.showhide_w.connect('notify::active', self.showhide)
    hbox.add(self.showhide_l)
    hbox.add(self.showhide_w)
    self.attach(hbox, 0, 1, 1, 1)

    # new ID button
    #self.newID_w = Gtk.Button('New ID')
    #self.newID_w.connect('clicked', self.newID)
    #self.attach(self.newID_w, 1, 0, 1, 2)

  def newID(self, *args):
    print button

  def showhide(self, *args):
    if(self.showhide_w.get_active()):
      self.passphrase.set_visibility(True)
    else:
      self.passphrase.set_visibility(False)

  def validate(self, *args):
    text = self.passphrase.get_text()
    words = text.split()
    if text.endswith(' '):
      words.append(' ') # so we treat a space as the start of a new word
    frac = min(1, len(words) / 12.0)

    self.passphrase.set_progress_fraction(frac)

    if(len(words) > 12):  # only 12 in electrum seed -- automatic bad
      self.passphrase.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'gtk-no')

    # validate that words are ok ... complex because they aren't ok while being typed
    bad = False
    for word in words[:-1]:
      if word not in electrum.mnemonic.words:
        self.passphrase.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'gtk-no')
        bad = True
        break
    if not bad and len(words) == 12 and words[-1] in electrum.mnemonic.words: # all good
      self.passphrase.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, 'gtk-yes')
    elif not bad:
      self.passphrase.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
    #print ('> "%s"' % text), len(text.split()), frac, args

class MyWindow(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, title="Deterministic ID")
    
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.add(vbox)

    # Add label describing what to do
    vbox.pack_start(Gtk.Label("Enter electrum seed:"),
        False, False, 0)

    # add ID passphrase entry (with options show passphrase, generate new ID)
    vbox.pack_start(PassphraseWidget(), False, False, 0)

    # add ListBox which contains children rows one per plugin with switch to enable/disable

    # add button to create ID for all checked plugins

    self.button = Gtk.Button(label="Generate!")
    #self.button.connect("clicked", self.generate?)
    vbox.pack_start(self.button, True, True, 0)

  def generate(self, widget):
    print("Stuff ...")

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
