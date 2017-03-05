'''
MenuItem Element

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Label

class MenuItem(Label):
  
  def __init__(self, x, y, label, fn):
    super(MenuItem, self).__init__(x, y, label)
    self.fn = fn

  def draw(self):
    super(MenuItem, self).draw()