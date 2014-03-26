#!/usr/bin/env python
import sys
import electrum
from gi.repository import Gtk

import plugin
import deterministicgpg

class PassphraseWidget(Gtk.Grid):
  def __init__(self):
    Gtk.Grid.__init__(self)
    self.set_vexpand(False)

    # passphrase field
    self.passphrase = Gtk.Entry(visibility=True, expand=True)
    self.passphrase.props.margin_bottom = 6
    self.passphrase.connect('changed', self.validate)
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
    if self.showhide_w.get_active():
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
      bad = True # we're good so far, but words are incomplete

    return not bad

  def get_seed(self):
    if not self.validate():
      raise Exception("Electrum seed incomplete")
    return electrum.mnemonic_decode(self.passphrase.get_text().split())


class PluginRow(Gtk.Box):
  def __init__(self, plugin):
    Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
    self.plugin = plugin
    self.props.margin_bottom = 12
    self.focus_widget = None

    # switch and expander
    self.switch = Gtk.Switch()
    self.pack_start(self.switch, False, False, 0)
    self.switch.connect('notify::active', self.on_off)
    self.expander = Gtk.Expander()
    self.pack_start(self.expander, True, True, 0)

    # header
    self.expander.set_label('<b>%s</b>' % self.plugin.title)
    self.expander.set_use_markup(True)

    # plugin
    self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    self.expander.add(self.box)

    # description
    label = Gtk.Label()
    label.set_line_wrap(True)
    label.set_markup('<small>%s</small>' % self.plugin.description)
    label.set_justify(Gtk.Justification.LEFT)
    label.props.halign = Gtk.Align.START
    label.props.xalign = 0
    label.props.margin_bottom = 6
    self.box.add(label)

    # plugin fields don't get done unless the switch gets flipped
    self.plugin_gui = False

  def create_plugin_gui(self):
    grid = Gtk.Grid()
    for i, field in enumerate(self.plugin.fields):
      entry = field.generate_widget()
      if i == 0: # first field, set focus
        self.focus_widget = entry

      # make a label for our new widget 
      label = Gtk.Label(field.gui_label)
      label.set_tooltip_markup(field.tip)
      label.props.margin_right = 12
      label.props.margin_left = 12
      label.props.halign = Gtk.Align.START
      grid.attach(label, 0, i, 1, 1)
      grid.attach(entry, 1, i, 1, 1)
    self.box.add(grid)
    self.box.show_all()

  def on_off(self, *args):
    if self.switch.get_active():
      if not self.plugin_gui: # create the plugin GUI
        self.create_plugin_gui()
        self.plugin_gui = True
      self.expander.set_expanded(True)
      if self.focus_widget:
        self.focus_widget.grab_focus()
    else:
      self.expander.set_expanded(False)

  def active(self):
    return self.switch.get_active()

  def processing(self, start):
    # would like some kind of feedback here ...
    # bigger issue is that the plugins are running in the GUI thread ...


plugins = [deterministicgpg.Plugin(),
    plugin.Plugin("Bar", "Some longer descriptions that is multiple lines.\nSecond line ..."),
    plugin.Plugin('Foo Bar Baz', 'A description <b>with</b> markup, line wrapping, and even a <a href="http://google.com">hyperlink</a>!  Wow!'),
    ]

class MainWindow(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, title="Deterministic ID")
    
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vbox.props.margin = 12
    self.add(vbox)

    # Add label describing what to do
    label = Gtk.Label("<b>Enter electrum seed:</b>", use_markup=True)
    label.props.halign = Gtk.Align.START
    label.props.valign = Gtk.Align.START
    label.props.vexpand = False
    vbox.pack_start(label, False, False, 0)

    # add ID passphrase entry (with options show passphrase, generate new ID)
    self.passphrase = PassphraseWidget()
    self.passphrase.props.valign = Gtk.Align.START
    vbox.pack_start(self.passphrase, False, False, 0)

    # add ListBox which contains children rows one per plugin with switch to enable/disable
    list_label = Gtk.Label("<b>Select types of IDs to generate</b>", use_markup=True)
    list_label.props.margin_top = 12
    list_label.props.margin_bottom = 6
    list_label.props.halign = Gtk.Align.START
    list_label.props.valign = Gtk.Align.START
    list_label.props.vexpand = False
    vbox.pack_start(list_label, False, False, 0)
    listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    listbox.props.margin_bottom = 6
    listbox.props.valign = Gtk.Align.START
    vbox.pack_start(listbox, True, True, 0)

    self.plugin_widgets = []
    for plugin in plugins:
      pr = PluginRow(plugin)
      pr.props.valign = Gtk.Align.START
      listbox.add(pr)
      self.plugin_widgets.append(pr)

    # add button to create ID for all checked plugins

    self.button = Gtk.Button(label="Generate!")
    self.button.valign = Gtk.Align.END
    self.button.connect("clicked", self.generate)
    vbox.pack_start(self.button, True, True, 0)

  def generate(self, widget):
    for pr in self.plugin_widgets:
      if pr.active() and pr.plugin.valid():
        pr.processing(True)
        pr.plugin.doit(self.passphrase.get_seed())
        pr.processing(False)

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
