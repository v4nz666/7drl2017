'''
MenuItem Element

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import List
from RoguePy.UI.Elements import MenuItem

class Menu(List):
  
  def __init__(self, x, y, w, h, menuItems=[]):
    super(Menu, self).__init__(x, y, w, h)

    self.selected = 0
    self.setWrap(True)

    self.menuItems = []
    self.itemStrings = []
    self.setItems(menuItems)

  def setItems(self, items):
    self.menuItems = []
    self.itemStrings = []
    _y = 0
    for i in items:
      label = i.keys()[0]
      fn = i[label]

      #if self.align == CENTER:
      print label
      _x = (self.width - len(label)) / 2
      #elif self.align == LEFT:
      #x = 0
      self.menuItems.append(MenuItem(_x, _y, label, fn))
      self.itemStrings.append(label)
    super(Menu, self).setItems(self.itemStrings)

  def setWrap(self, wrap):
    self._wrap = wrap
  def getWrap(self):
    return self._wrap
  
  def selectFn(self):
    # Call the associated callback, and pass the index that's just been selected.
    self.menuItems[self.selected].fn(self.selected)
  
  def selectUp(self):
    self._moveSelect(-1)
    return self
    
  def selectDown(self):
    self._moveSelect(1)
    return self
  
  def _moveSelect(self, step):
    newIndex = self.selected + step
    menuLength = len(self._items)
    wrapped = False

    if self._wrap:
      if newIndex < 0:
        newIndex = menuLength - 1
        self._offset = menuLength - self.height
        wrapped = True
      elif newIndex >= menuLength:
        newIndex = 0
        self._offset = 0
        wrapped = True

    else:
      if newIndex < 0:
        newIndex = 0
      elif newIndex >= menuLength:
        newIndex = menuLength - 1
    self.selected = newIndex
    if not wrapped:
      if self.selected >= self._offset + self.height:
        self.scrollDown()
      elif self.selected < self._offset:
        self.scrollUp()

    self.setDirty()

  def draw(self):
    if not len(self._items):
      return
    super(Menu, self).draw()
    y = self.selected - self._offset

    for x in range(len(self.menuItems[self.selected].getLabel())):
      selectedFg = libtcod.console_get_char_background(self.console, x, y)
      selectedBg = libtcod.console_get_char_foreground(self.console, x, y)
      libtcod.console_set_char_foreground(self.console, x, y, selectedFg)
      libtcod.console_set_char_background(self.console, x, y, selectedBg) 