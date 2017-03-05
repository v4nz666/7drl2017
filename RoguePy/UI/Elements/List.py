'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI import View
from RoguePy.UI.Elements import Element


class List(Element):
  
  def __init__(self, x, y, w, h, items=[]):
    if h == 0:
      h = len(items)
    super(List, self).__init__(x, y, w, h)
    self._items = items
    self._offset = 0

  def setItems(self, items):
    self.clear()
    self._items = items
    self.setDirty()

  def addItem(self, item):
    self._items.append(item)
    self.setDirty()

  def removeItem(self, item):
    if item in self._items:
      self._items.remove(item)
    self.setDirty()

  def scroll(self,step):
    newOffset = self._offset + step
    if len(self._items) - newOffset >= self.height and newOffset >= 0:
      self._offset = newOffset
    self.setDirty()
  def scrollUp(self,step=1):
    self.scroll(-step)
  def scrollDown(self, step=1):
    self.scroll(step)

  def draw(self):
    for y in range(self.height):
      index = y + self._offset
      if index >= len(self._items):
        continue
      item = self._items[index]
      libtcod.console_print(self.console, 0, y, item)
    if self._offset > 0:
      libtcod.console_put_char(self.console, self.width - 1, 0, libtcod.CHAR_ARROW_N)
    if len(self._items) > self._offset + self.height:
      libtcod.console_put_char(self.console, self.width - 1, self.height - 1, libtcod.CHAR_ARROW_S)
    self.setDirty(False)