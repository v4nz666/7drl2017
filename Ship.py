import sys

import config
from RoguePy.libtcod import libtcod
from RoguePy.Game import Entity
from shipTypes import shipTypes


class Ship(Entity):
    def __init__(self, map, type, x, y, color, isPlayer=False):
        self.name = type
        # for attr, value in shipTypes[type].iteritems():
        #     setattr(self, attr, value)
        self.ch = '@'
        self.anchored = True
        self.hullDamage = 0
        self.sailDamage = 0
        self.heading = 0.0
        self.headingRad = 0.0
        self.sails = 0
        self.speed = 0.0
        self.crew = 0

        self.stats = type

        self.canSee = True
        self.viewRadius = 8

        self.x = x
        self.y = y

        super(Ship, self).__init__(map, self.mapX, self.mapY, self.name, self.ch, color)

        self.isPlayer = isPlayer

        # To be overridden by shipTypes
        self.maxSpeed = 0
        self.turnSpeed = 0
        self.guns = 0
        self.minCrew = 0
        self.maxCrew = 0
        self.size = 0
        self.price = 0

        for attr, value in shipTypes[type].iteritems():
            setattr(self, attr, value)

        self.goods = {
            'food': 0,
            'rum': 0,
            'wood': 0,
            'cloth': 0,
            'coffee': 0,
            'spice': 0
        }

        self.inHold = 0

        self._initFovMap()
        self.calculateFovMap()

    def addGoods(self, item):
        if item not in self.goods:
            return False

        self.goods[item] += 1
        self.inHold += 1
        if self.inHold > self.size:
            self.goods[item] -= 1
            self.inHold -= 1
            return False
        return True

    def takeGoods(self, item):
        if item not in self.goods:
            return False
        if self.goods[item] < 1:
            return False

        self.goods[item] -= 1
        self.inHold -= 1
        return True

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, x):
        self.__x = x
        self.mapX = int(round(x))

    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self, y):
        self.__y = y
        self.mapY = int(round(y))

    def toggleAnchor(self):
        self.anchored = not self.anchored

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
            self.fovMap, self.mapX, self.mapY, self.viewRadius, True, libtcod.FOV_SHADOW
        )
        for _y in range(-self.viewRadius, self.viewRadius + 1):
            for _x in range(-self.viewRadius, self.viewRadius + 1):
                if self.isPlayer:
                    x = self.mapX + _x
                    y = self.mapY + _y
                    c = self.map.getCell(x, y)
                    if c and self.inSight(x, y):
                        c.seen = True

    def inSight(self, x, y):
        return libtcod.map_is_in_fov(self.fovMap, x, y)

    def sailAdjust(self, step):
        newSails = max(min(self.sails + step, config.maxSails), 0)
        if newSails != self.sails:
            self.sails = newSails
            self.speed = config.sailStep * self.sails * self.maxSpeed

    def headingAdjust(self, val):
        self.heading += val
        if self.heading < 0:
            self.heading += 360
        elif self.heading >= 360:
            self.heading -= 360
