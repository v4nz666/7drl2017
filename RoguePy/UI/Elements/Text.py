'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element

class Text(Element):
  
  def __init__(self, x, y, w, h, text=b""):
    super(Text, self).__init__(x, y, w, h)
    self._text = text
  
  def setText(self, text):
    self._text = text
    self.setDirty()
    return self
    
  def draw(self):
    libtcod.console_print_rect(self.console, 0, 0, self.width, self.height, self._text)
    self.setDirty(False)
