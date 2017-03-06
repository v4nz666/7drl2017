"""
Documentation, License etc.

@package RoguePy.UI
"""
from RoguePy.libtcod import libtcod
from RoguePy.UI import View

class Element(View):
  #TODO we should be calling View.__init__  :/
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.width = w
    self.height = h

    self.visible = True
    self.enabled = True

    self.setDirty(True)

    self.console = libtcod.console_new(w, h)

    self.setDefaultColors()
    self.clear()

    self._elements = []
    self._keyBoardInputs = {}
    self._mouseInputs = {
      'rClick': None,
      'lClick': None
    }


    self.fgOpacity = 1
    self.bgOpacity = 1
    self.parent = None

    self.fg = libtcod.white
    self.bg = libtcod.black

    self.bgFlag = libtcod.BKGND_SET

  def setParent(self, parent):
    self.parent = parent

  def draw(self):
    pass

  def toggleVisible(self):
    self.visible = not self.visible
    if self.visible:
      self.setDirty()

    return self
  def show(self):
    self.visible = True
    self.setDirty()
    return self
  def hide(self):
    self.visible = False
    return self

  ###
  def toggleEnabled(self):
    self.enabled = not self.enabled
    self.setDirty()
    return self

  def enable(self):
    self.enabled = True
    self.setDirty()
    return self

  def disable(self):
    self.enabled = False
    self.setDirty()
    return self