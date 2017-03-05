'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element
class Modal(Element):
  
  def __init__(self, x, y, w, h):
    super(Modal, self).__init__(x, y, w, h)
    self.enabled = False
    self.visible = False
    
  def show(self, view):
    view.storeState()
    view.disableAll()
    self.visible = True
    self.enabled = True
    self.setDirty()
  
  def hide(self, view):
    self.visible = False
    self.enabled = False
    self.onClose()
    view.restoreState()
    view.enableInputs()
  
  def onClose(self):
    pass