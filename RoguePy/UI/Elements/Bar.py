'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element

class Bar(Element):
  
  def __init__(self, x, y, w, h=1):
    super(Bar, self).__init__(x, y, w, h)

    self.setMin(0)
    self.setMax(100)
    self.setVal(100)
    
    self.chars = [
      libtcod.CHAR_BLOCK1,
      libtcod.CHAR_BLOCK2,
      libtcod.CHAR_BLOCK3
    ]
    
    self._fgMin = libtcod.white
    self._fgMax = libtcod.white
    self._bgMin = libtcod.black
    self._bgMax = libtcod.black

  def setMin(self, min):
    self._min = min
    return self
  def setMax(self,max):
    self._max = max
    return self
  def getMin(self):
    return self._min
  def getMax(self):
    return self._max
  
  def setVal(self,val):
    if val > self._max:
      val = self._max
    elif val < self._min:
      val = self._min
    self._val = val
    self.setDirty()
    return self

  def getVal(self):
    return self._val
  
  def setChars(self,chars):
    self.chars = chars
    return self
  def getChars(self):
    return self.chars
  
  def calculateColors(self):
    self._colors = []
    length = self.width * len(self.chars)
    for i in range(length):
      coef = i / float(length)
      fg = libtcod.color_lerp(self._fgMin, self._fgMax, coef)
      bg = libtcod.color_lerp(self._bgMin, self._bgMax, coef)
      self._colors.append((fg, bg))

  def setMinColor(self, fg, bg=libtcod.black):
    self._fgMin = fg
    self._bgMin = bg
    self.calculateColors()
    return self
  def setMaxColor(self, fg, bg=libtcod.black):
    self._fgMax = fg
    self._bgMax = bg
    self.calculateColors()
    return self
  
  def draw(self):
    
    _max = float(self._max - self._min)
    val = self._val - self._min

    if val <= 0:
      return

    chars = len(self.chars)
    steps = self.width * chars
    
    if steps != len(self._colors):
      self.calculateColors()
      
    fullSteps = int(val / _max * steps)
    fullChars = int(fullSteps / chars)
    
    lastChar = self.chars[fullSteps % chars]
    
    colorIndex = max(0, min(len(self._colors) - 1, val-1))

    fg = self._colors[colorIndex][0]
    bg = self._colors[colorIndex][1]
    
    for y in range(self.height):
      for i in range(fullChars):
        libtcod.console_put_char_ex(self.console, i, y, self.chars[-1], fg, bg)
      libtcod.console_put_char_ex(self.console, fullChars, y, lastChar, fg, bg)

    self.setDirty(False)