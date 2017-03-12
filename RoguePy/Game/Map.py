import sys

import config
import util
from RoguePy.libtcod import libtcod
from RoguePy.UI import Colors
from City import City


class Map:
    def __init__(self, w, h, cells=None):
        self.width = w
        self.height = h
        if cells == None:
            self.cells = [Cell('floor') for dummy in range(w*h)]
        else:
            self.cells = cells
        self.listeners = {}
        self.cities = {}

    @staticmethod
    def FromHeightmap(hm, thresholds):
        mapMin, mapMax = libtcod.heightmap_get_minmax(hm)
        mapMax = mapMax - mapMin

        w = config.world['width']
        h = config.world['height']

        cells = []

        for c in range(w*h):
            x = c % w
            y = c / w

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
        #     lookups for different map data files / strings.
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
        try:
            return self.cells[x + y * self.width]
        except IndexError:
            return False

    def on(self, eventName, fn):
        eventListeners = self.listeners.get(eventName)
        if eventListeners == None:
            eventListeners = []
            self.listeners[eventName] = eventListeners
        eventListeners.append(fn)

    def trigger(self, eventName, sender, e):
        # print "'%s' triggered by %s" % (eventName, sender), "e = ", e
        eventListeners = self.listeners.get(eventName)
        if not eventListeners:
            return
        for listener in eventListeners:
            listener(sender, e)

    def getNeighboursOfType(self, type, x, y):
            neighbours = self.getNeighbours(x, y)
            toPurge = []
            for neighbourX, neighbourY in neighbours:
                c = neighbours[neighbourX, neighbourY]
                if c.type != type:
                    toPurge.append(c)

            neighbours = {k: v for k, v in neighbours.items() if v not in toPurge}
            if len(neighbours):
                return neighbours
            else:
                return {}

    def getNeighbours(self, x, y, diagonals=True):
        cells = {}
        for dx in range(-1, 2):
            for dy in range(-1,2):
                neighbourX = x + dx
                neighbourY = y + dy
                if not diagonals and (not neighbourX or not neighbourY):
                    continue
                c = self.getCell(neighbourX, neighbourY)
                if c:
                    cells[neighbourX, neighbourY] = c
        return cells

    # Hard coded 1 entity per tile
    def removeEntity(self, e, x, y):
        c = self.getCell(x, y)
        if c.entity == e:
            c.entity = None
            return True
        return False

    def addEntity(self, e, x, y):
        c = self.getCell(x, y)
        if c.entity is None:
            self.getCell(x, y).entity = e
            if e.canSee:
                e.calculateFovMap()
            return e
        return False

    ### Pirates hacks
    def addCity(self, x, y, portX, portY, name):
        c = City(self, x, y, name, portX, portY, '#', Colors.black)

        self.addEntity(c, x, y)
        self.getCell(portX, portY).isPort = True

        self.cities[name] = c

        return c

    def getMajorCities(self):
        cities = []
        for name in self.cities:
            city = self.cities[name]
            if city.size == 4:
                cities.append(city)
        return cities

    def initCityNeighbours(self):
        for source in self.cities:
            neighbours = []
            city = self.cities[source]
            for target in self.cities:
                neighbour = self.cities[target]
                if neighbour != city and city.inSight(neighbour.x, neighbour.y):
                    neighbours.append(self.cities[target])
            city.neighbours = neighbours


class Cell:
    def __init__(self, typeName):
        self.type = typeName
        self.terrain = CellType.All[typeName]
        self.entity = None
        self.isPort = False
        self.seen = False

        self.items = []
        pass

    def __str__(self):
        attributes = ''
        for attr, value in self.__dict__.iteritems():
            attributes += '    {}: {}\n'.format(attr, value)
        return 'Cell [{}]\n{}'.format(self.type, attributes)


class CellType:
    def __init__(self, char, fg, bg, opts):
        self.char = char
        self.fg = fg
        self.bg = bg
        for opt in opts:
                setattr(self, opt, opts[opt])

    def __str__(self):
        attributes = ''
        for attr, value in self.__dict__.iteritems():
            attributes += '        {}: {}\n'.format(attr, value)
        return 'Cell Type\n{}'.format(attributes)

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
    'destructible': False,
}
mountain = {
    'passable': False,
    'transparent': False,
    'destructible': True,
}

# TODO: This is game-specific.
CellType.All = {
    'water': CellType('~', Colors.blue, Colors.dark_blue, water),
    'grass': CellType('[', Colors.darker_green, libtcod.Color(0, 96, 0), grass),
    'tree': CellType('&', Colors.darkest_green, libtcod.Color(0, 96, 0), tree),
    'mountain': CellType('^', Colors.darker_grey, libtcod.Color(0, 96, 0), mountain),
}