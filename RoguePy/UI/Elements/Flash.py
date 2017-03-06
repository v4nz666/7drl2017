"""
Documentation, License etc.

@package RoguePy.UI
"""
from RoguePy.UI.Elements import Animation
class Flash(Animation):
  
  def __init__(self, x, y, w, h):
    super(Flash, self).__init__(x, y, w, h, 600)
    self.visible = False
    self.bgOpacity = 0
  
  def getFrame(self, currentFrame):
    self.fgOpacity = 1 - (currentFrame / float(self._frameCount))