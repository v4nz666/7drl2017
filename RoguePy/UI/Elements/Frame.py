'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element

class Frame(Element):
  
  def __init__(self, x, y, w, h, title=""):
    super(Frame, self).__init__(x, y, w, h)
    
    self.setTitle(title);
    
    self._chars = {
      'tl': libtcod.CHAR_NW,
      't' : libtcod.CHAR_HLINE,
      'tr': libtcod.CHAR_NE,
      'r' : libtcod.CHAR_VLINE,
      'br': libtcod.CHAR_SE,
      'b' : libtcod.CHAR_HLINE,
      'bl': libtcod.CHAR_SW,
      'l' : libtcod.CHAR_VLINE
    }
  
  def setTitle(self, title):
    if len(title) > self.width-2:
      title = title[:self.width-2]
    self._title = title
    self.setDirty()
    return self

  def draw(self):
    for y in range(self.height):
      for x in range(self.width):
        #top row
        if y == 0:
          if x == 0:
            ch = self._chars['tl']
          elif x == self.width - 1:
            ch = self._chars['tr']
          else:
            ch = self._chars['t']
        #bottom row
        elif y == self.height - 1:
          if x == 0:
            ch = self._chars['bl']
          elif x == self.width - 1:
            ch = self._chars['br']
          else:
            ch = self._chars['b']
        #middle rows
        else:
          if x == 0:
            ch = self._chars['l']
          elif x == self.width - 1:
            ch = self._chars['r']
          else:
            ch = None
        if ch:
          libtcod.console_put_char(self.console, x, y, ch)
    libtcod.console_print(self.console, 1, 0, self._title)

    self.setDirty(False)