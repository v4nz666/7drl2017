import chars
import config
from RoguePy.libtcod import libtcod
from RoguePy.UI import Colors


class Map:
  def __init__(self, w, h, cells=None):
    self.width = w
    self.height = h
    if cells == None:
      self.cells = [Cell('floor') for dummy in range(w*h)]
    else:
      self.cells = cells
    self.listeners = {}

  @staticmethod
  def FromHeightmap(hm, thresholds):
    mapMin, mapMax = libtcod.heightmap_get_minmax(hm)
    mapMax = mapMax - mapMin

    w = config.world['width']
    h = config.world['height']

    cells = []

    for c in range(w*h):
      x = c%w
      y = c/w

      v = libtcod.heightmap_get_value(hm, x, y)
      for t in thresholds:
        if v <= t['range'] * mapMax:
          cells.append(Cell(t['type']))
          break
    return Map(w, h, cells)

  @staticmethod
  def FromFile(path):
    lines = open(path).read().splitlines()
    return Map.FromStringList(lines)

  @staticmethod
  def FromStringList(lines):
    # Get map dimensions, while ensuring all lines are the same length.
    w = None
    linenum = 0
    for x in lines:
      if w == None:
        w = len(x)
      elif len(x) != w:
        raise Exception("Line(%d) length = %d, expected = %d" % (linenum, len(x), w))
      linenum += 1
    h = len(lines)

    # Convert characters into map cells.
    cells = []
    for row in lines:
      for ch in row:
        cells.append(Map.CharToCell(ch))
    return Map(w, h, cells)

  @staticmethod
  def CharToCell(ch):
    # TODO: This is not only game-specific, it's LOAD specific. No reason not to allow different
    #   lookups for different map data files / strings.
    cell = {
      '#': Cell('wall'),
      '.': Cell('floor'),
      'd': Cell('door'),
      'w': Cell('window'),
    }.get(ch)
    if cell == None:
      raise Exception("Unknown cell token [" + ch + "]")
    return cell

  def getCell(self, x, y):
    # TODO: Bounds checking.
    return self.cells[x + y * self.width]

  def on(self, eventName, fn):
    eventListeners = self.listeners.get(eventName)
    if eventListeners == None:
      eventListeners = []
      self.listeners[eventName] = eventListeners
    eventListeners.append(fn)

  def trigger(self, eventName, sender, e):
    # print "'%s' triggered by %s" % (eventName, sender), "e = ", e
    eventListeners = self.listeners.get(eventName)
    if not eventListeners: return
    for listener in eventListeners:
      listener(sender, e)


class Cell:
  def __init__(self, type):
    self.type = type
    self.terrain = CellType.All[type]
    self.entity = None
    self.items = []
    pass

class CellType:
  def __init__(self, char, fg, bg, opts):
    self.char = char
    self.fg = fg
    self.bg = bg
    self.opts = opts

water = {
  'passable': True,
  'transparent': True,
  'destructible': False,
}
grass = {
  'passable': False,
  'transparent': True,
  'destructible': False,
}
tree = {
  'passable': False,
  'transparent': True,
  'destructible': True,
}
mountain = {
  'passable': False,
  'transparent': False,
  'destructible': True,
}


# TODO: This is game-specific.
CellType.All = {
    'water': CellType(b'~', Colors.blue, Colors.dark_blue, water),
    'grass': CellType(b'.', Colors.dark_green, Colors.darker_green, grass),
    'mountain': CellType('^', Colors.white, Colors.darker_green, mountain),
}
