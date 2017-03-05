
from RoguePy.libtcod import libtcod


class Terrain:
  def __init__(self, see, walk, desc):
    """
    :type see: bool
    :type walk: bool
    :type desc: string
    """
    self.see = see
    self.walk = walk
    self.desc = desc

    self.char = ' '
    self.fg = libtcod.black
    self.bg = libtcod.black

  def setChar(self, char):
    self.char = char
    return self
  def setColors(self, fg, bg = libtcod.black):
    self.fg = fg
    self.bg = bg
    return self

  def __repr__(self):
    return str((self.see, self.walk, self.desc))