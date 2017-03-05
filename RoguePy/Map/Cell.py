import terrains


class Cell(object):
  def __init__(self, terrain = terrains.EMPTY):
    """
    Cell class. Represents one space on the Map

    :return: self
    """
    self.terrain = terrain
    self.entity = None
    self.items = []


  def setTerrain(self, terrain):
    self.terrain = terrain

  def transparent(self):
    return self.terrain.see

  def passable(self):
    return self.terrain.walk
