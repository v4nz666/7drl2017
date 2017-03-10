import sys

import config
from RoguePy.libtcod import libtcod
from RoguePy.Game import Entity
from shipTypes import shipTypes


class Ship(Entity):
    def __init__(self, map, type, x, y, isPlayer=False, stats=None):
        self.name = type

        if stats is None:
            self.stats = shipTypes[type]
        else:
            self.stats = stats

        self.ch = '@'

        self.isPlayer = isPlayer
        self.x = x
        self.y = y

        super(Ship, self).__init__(map, self.mapX, self.mapY, self.name, self.ch, self.stats['color'], True, 8, isPlayer)

        self.anchored = True
        self.heading = 0.0
        self.headingRad = 0.0
        self.sails = 0
        self.speed = 0.0
        self.crew = 0

        self.cannonballs = 0
        self.chainshot = 0

        self.goods = {
            'food': 0,
            'rum': 0,
            'wood': 0,
            'cloth': 0,
            'coffee': 0,
            'spice': 0
        }

        self.inHold = 0

    @staticmethod
    def getBuyPrice(stats):
        return int(config.economy['buyMul'] * Ship._getValue(stats))

    @staticmethod
    def getSellPrice(stats):
        return int(config.economy['sellMul'] * Ship._getValue(stats))

    def addCannonballs(self, count):
        if self.inHold + count > self.stats['size']:
            return False
        self.cannonballs += count
        self.inHold += count
        return True

    def addChainshot(self, count):
        if self.inHold + count > self.stats['size']:
            return False
        self.chainshot += count
        self.inHold += count
        return True

    @staticmethod
    def _getValue(stats=None):
        if stats is None:
            stats = shipTypes[type]
        value = stats['price']
        if stats['hullDamage'] > 0:
            value -= int(stats['hullDamage'] / 100.0 * stats['price'] * 2/3)

        if stats['sailDamage'] > 0:
            value -= int(stats['sailDamage'] / 100.0 * stats['price'] * 1/3)
        return value

    def addGoods(self, item):
        if item not in self.goods:
            return False
        self.goods[item] += 1
        self.inHold += 1
        if self.inHold > self.stats['size']:
            self.goods[item] -= 1
            self.inHold -= 1
            return False
        return True

    def takeGoods(self, item):
        if item not in self.goods:
            return False
        if self.goods[item] < 1:
            return False
        print "selling {}".format(item)
        self.goods[item] -= 1
        print " left {}".format(self.goods[item])

        self.inHold -= 1
        print " Total in hold {}".format(self.inHold)
        print " Goods:{}".format(self.goods)
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

    def sailAdjust(self, step):
        newSails = max(min(self.sails + step, config.maxSails), 0)
        if newSails != self.sails:
            self.sails = newSails
            self.speed = config.sailStep * self.sails * self.stats['maxSpeed']

    def headingAdjust(self, val):
        self.heading += val
        if self.heading < 0:
            self.heading += 360
        elif self.heading >= 360:
            self.heading -= 360

    def repairHull(self):
        if not self.stats['hullDamage']:
            return False
        self.stats['hullDamage'] -= config.shipyard['repairReturn']
        if self.stats['hullDamage'] < 0:
            self.stats['hullDamage'] = 0

        return True

    def repairSails(self):
        if not self.stats['sailDamage']:
            return False
        self.stats['sailDamage'] -= config.shipyard['repairReturn']
        if self.stats['sailDamage'] < 0:
            self.stats['sailDamage'] = 0
        return True