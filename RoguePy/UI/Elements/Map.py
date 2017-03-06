from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element
from collections import namedtuple
from .. import Colors

CellView = namedtuple('CellView', ['char', 'fg', 'bg'])

class Map(Element):
  def __init__(self, x, y, w, h, _map):
    super(Map, self).__init__(x, y, w, h)
    self._map = _map
    self._offsetX = 0
    self._offsetY = 0
    self.halfW = self.width / 2
    self.halfH = self.height / 2

  def center(self, x, y):
    """
    Centers the view-port of the ui element around coordinates x, y of the map. If the coordinate is near the edge of
    the map, the actual center of the view-port will differ from those passed in. 
    
    See also: onScreen() - Return the onscreen coordinates of a given x, y pair accounting for centering.
    
    :param x: X coordinate to center view around
    :param y: Y coordinate to center view around
    :return: self
    """
    if x < self.halfW:
      self._offsetX = 0
    elif x < self._map.width - self.halfW:
      self._offsetX = x - self.halfW
    else:
      self._offsetX = self._map.width - self.width
    
    if y < self.halfH:
      self._offsetY = 0
    elif y < self._map.height - self.halfH:
      self._offsetY = y - self.halfH
    else:
      self._offsetY = self._map.height - self.height
    self.setDirty()
    return self

  def fromScreen(self, sx, sy):
    """
    Return the map coordinates of a given onscreen x, y pair accounting for centering.

    :param sx: int   The on screen X coordinate to calculate the map coordinate of.
    :param sy: int   The on screen X coordinate to calculate the map coordinate of.
    :return: tuple|bool  Adjusted (x, y) coordinates; False if the given x, y coordinates lie outside this element
    """

    if sx < self.x or sx >= self.x + self.width:
        sx = False
    if sy < self.y or sy >= self.y + self.height:
        sy = False

    mapX = sx + self._offsetX - self.x
    mapY = sy + self._offsetY - self.y

    if sx and sy:
        return mapX, mapY
    else:
        return -1, -1

  def onScreen(self, x, y):
    """
    Return the onscreen coordinates of a given x, y pair accounting for centering.

    :param x: int   The actual map X coordinate to calculate the onscreen coordinate of.
    :param y: int   The actual map X coordinate to calculate the onscreen coordinate of.
    :return: tuple  Adjusted (x, y) coordinates
    """
    return x - self._offsetX, y - self._offsetY
  
  def draw(self):
    for sy in range(self.height):
      for sx in range(self.width):
        x = sx + self._offsetX
        y = sy + self._offsetY
        if (x >= 0 and x < self._map.width and y >= 0 and y < self._map.height):
          c = self._map.getCell(x, y)
          if not c:
              continue
          cv = self.cellToView(c)
          libtcod.console_put_char_ex(self.console, sx, sy, cv.char, cv.fg, cv.bg)

    self.setDirty(False)

  def cellToView(self, c):
    result = CellView(c.terrain.char, c.terrain.fg, c.terrain.bg)
    if c.entity != None:
      result = CellView(c.entity.ch, c.entity.fg, result.bg)
    elif c.items:
      pass
    return result

  # TODO: Does this belong here, or in View? It's a bit hackish because we only want to replace
  #   a subset of the inputs, not the whole input set.
  # TODO: If input binding is streamlined, this won't work anymore.
  def setDirectionalInputHandler(self, fn):
    print "Inputs set"
    from RoguePy.Input import Keys
    self._keyBoardInputs['move_sw'] = {
        'key' : Keys.NumPad1,
        'ch'  : None,
        'fn'  : lambda: fn(-1,1)
    }
    self._keyBoardInputs['move_s'] = {
        'key' : Keys.NumPad2,
        'ch'  : None,
        'fn'  : lambda: fn(0,1)
    }
    self._keyBoardInputs['move_se'] = {
        'key' : Keys.NumPad3,
        'ch'  : None,
        'fn'  : lambda: fn(1,1)
    }
    self._keyBoardInputs['move_w'] = {
        'key' : Keys.NumPad4,
        'ch'  : None,
        'fn'  : lambda: fn(-1,0)
    }
    self._keyBoardInputs['move_none'] = {
        'key' : Keys.NumPad5,
        'ch'  : None,
        'fn'  : lambda: fn(0,0)
    }
    self._keyBoardInputs['move_e'] = {
        'key' : Keys.NumPad6,
        'ch'  : None,
        'fn'  : lambda: fn(1,0)
    }
    self._keyBoardInputs['move_nw'] = {
        'key' : Keys.NumPad7,
        'ch'  : None,
        'fn'  : lambda: fn(-1,-1)
    }
    self._keyBoardInputs['move_n'] = {
        'key' : Keys.NumPad8,
        'ch'  : None,
        'fn'  : lambda: fn(0,-1)
    }
    self._keyBoardInputs['move_ne'] = {
        'key' : Keys.NumPad9,
        'ch'  : None,
        'fn'  : lambda: fn(1,-1)
    }
