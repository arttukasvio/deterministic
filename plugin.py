from gi.repository import Gtk

class Field(object):
  def __init__(self, cmdline, gui_label, tip):
    self.cmdline = cmdline
    self.gui_label = gui_label
    self.tip = tip
    self.value = None

  def validate(self, newval):
    return True

  def generate_widget(): pass

class StringField(Field):
  def generate_widget(self):
    entry = Gtk.Entry()
    def handle(*args):
      text = entry.get_text()
      if self.validate(text):
        self.value = text
    entry.connect('changed', handle)
    return entry

#Incomplete
class ReStringField(StringField):
  def validate(self, newval):
    pass

class UIntField(Field):
  def validate(self, newval):
    return newval.isdigit()

  def generate_widget(self):
    entry = Gtk.SpinButton()
    entry.set_numeric(True)
    entry.set_adjustment(Gtk.Adjustment(0, 0, sys.maxint, 1, 100, 0))
    entry.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
    def handle(*args):
      print entry.get_value_as_int()
      self.value = entry.get_value_as_int()
    entry.connect('value-changed', handle)
    return entry

class Plugin(object):
  def __init__(self, title, description):
    self.title = title
    self.description = description
    self.fields = [StringField('so', 'Foo Var:', 'a tip')]

  def doit(self, seed): pass

