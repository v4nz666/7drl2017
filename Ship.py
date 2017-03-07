import sys

from RoguePy.libtcod import libtcod
from RoguePy.Game import Entity
from shipTypes import shipTypes


class Ship(Entity):
    def __init__(self, map, type, x, y, color, isPlayer=False):
        self.name = type
        for attr, value in shipTypes[type].iteritems():
            setattr(self, attr, value)
        self.ch = '@'
        self.anchored = True
        self.hullDamage = 0
        self.sailDamage = 0
        self.heading = 0
        self.sails = 0

        self.canSee = True
        self.viewRadius = 5
        super(Ship, self).__init__(map, x, y, self.name, self.ch, color)

        self.isPlayer = isPlayer

        self._initFovMap()
        self.calculateFovMap()

    def _initFovMap(self):
        w, h = self.map.width, self.map.height
        self.fovMap = libtcod.map_new(w, h)
        for y in range(h):
            for x in range(w):
                c = self.map.getCell(x, y)
                if c:
                    libtcod.map_set_properties(self.fovMap, x, y, c.terrain.transparent, c.terrain.passable)

    def calculateFovMap(self):
        libtcod.map_compute_fov(
            self.fovMap, self.x, self.y, self.viewRadius, True, libtcod.FOV_SHADOW
        )
        for _y in range(-self.viewRadius, self.viewRadius + 1):
            for _x in range(-self.viewRadius, self.viewRadius + 1):
                if self.isPlayer:
                    x = self.x + _x
                    y = self.y + _y
                    c = self.map.getCell(x, y)
                    if c and self.inSight(x, y):
                        c.seen = True

    def inSight(self, x, y):
        return libtcod.map_is_in_fov(self.fovMap, x, y)
