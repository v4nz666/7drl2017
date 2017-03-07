'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element
class Animation(Element):
  
  def __init__(self, x, y, w, h, frameCount, loop=False):
    super(Animation, self).__init__(x, y, w, h)
    self._frameCount = frameCount
    self._currentFrame = 0
    self._loop = loop
    
  def updateAnimationFrame(self):
    self.getFrame(self._currentFrame)
    self._currentFrame += 1
    if self._currentFrame >= self._frameCount:
      if self._loop:
        self._currentFrame = 0
      else:
        self.onFinish()
        self.hide()
  
  def getFrame(self, frame):
    pass
  
  def onFinish(self):
    pass