'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element

class Slider(Element):
  
  def __init__(self, x, y, w, min, max, val=0, step=1):
    self.min = min
    self.max = max
    self.__val = val
    self.step = step

    super(Slider, self).__init__(x, y, w, 1)
    self.sliderWidth = self.width - 2
    self.valPerChar = (self.max - self.min) / self.sliderWidth
    self.setChars(['<','-','>','|'])

  @property
  def min(self):
    return self.__min
  @min.setter
  def min(self, min):
    self.__min = min
  
  @property
  def max(self):
    return self.__max
  @max.setter
  def max(self, max):
    self.__max = max
  
  @property
  def val(self):
    return self.__val
  @val.setter
  def val(self, val):
    if val > self.max:
      val = self.max
    elif val < self.min:
      val = self.min
    if val != self.val:
      self.__val = val
      self.onChange()
      self.setDirty()
  
  @property
  def step(self):
    return self.__step
  @step.setter
  def step(self, step):
    self.__step = step
  
  def onChange(self):
    pass
  
  def setChars(self, chars):
    if not len(chars) == 4:
      raise IndexError("chars list must contain 4 elements")
    self._left = chars[0]
    self._center = chars[1]
    self._right = chars[2]
    self._bar = chars[3]

  def left(self):
    self.val = self.val - self.step
  def right(self):
    self.val = self.val + self.step
  
  def draw(self):
    libtcod.console_put_char(self.console, 0, 0,self._left)
    for x in range(self.sliderWidth):
      libtcod.console_put_char(self.console, x + 1, 0, self._center)
    libtcod.console_put_char(self.console, self.width - 1, 0, self._right)
    sliderPosition = min(self.sliderWidth - 1, self.val / self.valPerChar)
    libtcod.console_put_char(self.console, sliderPosition + 1, 0, self._bar)

    self.setDirty(False)
