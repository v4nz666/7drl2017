from RoguePy.libtcod import libtcod
from Cell import Cell


class Map(object):


  def __init__(self, w, h):
    self.width = w
    self.height = h

    self._map = libtcod.map_new(w, h)
    self.cells = [Cell() for coord in range(self.width * self.height)]

  def getCell(self, x, y):
    return self.cells[x + y * self.width]

  def getTerrain(self, x, y):
    return self.getCell(x, y).terrain
