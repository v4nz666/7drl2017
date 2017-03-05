'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element

class Label(Element):
  
  def __init__(self, x, y, label="", width=None):
    if width:
      w = width
    else:
      w = len(label)
    super(Label, self).__init__(x, y, w, 1)
    self._label = label
  
  def setLabel(self, label):
    if self._label == label:
      pass

    if len(label) > self.width:
      label = label[self.width:]

    self._label = label
    self.setDirty()

  def getLabel(self):
    return self._label
  
  def draw(self):
    libtcod.console_print(self.console, 0, 0, self._label)
    self.setDirty(False)