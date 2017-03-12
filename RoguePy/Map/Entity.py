from RoguePy.UI import Colors

class Entity(object):
  def __init__(self, name):
    self.name = name
    self.ch = ' '
    self.fg = Colors.black

  def setChar(self, ch):
    self.ch = ch

  def setColor(self, color):
    self.fg = color
