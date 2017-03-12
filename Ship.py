import sys

import config
import util
from Projectile import Projectile
from RoguePy.libtcod import libtcod
from RoguePy.Game import Entity
from shipTypes import shipTypes
from util import randint

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
        self.sunk = False
        self.reloading = False
        self.coolDown = 0

        self.maxSails = config.maxSails
        
        placed = False
        attempts = 0
        while not placed:
            try:
                super(Ship, self).__init__(
                    map, self.mapX, self.mapY, self.name, self.ch, self.stats['color'], True, config.ship['minView'], isPlayer)
                placed = True
            except:
                dx, dy = 0, 0
                while not (dx or dy):
                    dx = randint(1, -1)
                    dy = randint(1, -1)
                # failed attempt (no water, don't count it)
                if not map.getCell(self.mapX + dx, self.mapY + dy).terrain.passable:
                    continue

                attempts += 1
                print "trying again"
                if attempts >= 10:
                    print "too many tries, aborting"
                    raise ShipPlacementError

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
    
    def damageHull(self, dmg):
        self.stats['hullDamage'] += dmg
        if self.stats['hullDamage'] >= 100:
            self.stats['hullDamage'] = 100
            self.sunk = True
    
    def damageSails(self, dmg):
        self.stats['sailDamage'] += dmg
        if self.stats['sailDamage'] >= 100:
            self.stats['sailDamage'] = 100
        self.maxSails = int(self.stats['sailDamage']/100.0 * config.maxSails)
        print "Sails damaged by {}. New max {}".format(dmg, self.maxSails)

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
    def _getValue(stats):
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

    @property
    def sails(self):
        return self.__sails
    @sails.setter
    def sails(self, sails):
        self.__sails = sails
        self.speed = config.sailStep * self.__sails * self.stats['maxSpeed']

    def toggleAnchor(self):
        self.anchored = not self.anchored

    def sailAdjust(self, step):
        newSails = max(min(self.sails + step, self.maxSails), 0)
        if newSails != self.sails:
            self.sails = newSails

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

    def canFire(self, x, y):
        print "Checking firing status"
        if self.reloading:
            print "can't fire. reloading"
            return False

        bearing = util.bearing(self.mapX, self.mapY, x, y)
        bearing = self.heading - bearing
        if bearing < 0:
            bearing += 180
        elif bearing >= 180:
            bearing -= 180
        print "after {}".format(bearing)
        if 50 <= abs(bearing) <= 130:
            print "firing from {},{} -> {},{}".format(self.mapX, self.mapY, x, y)
            return True
        else:
            print "outside cone"
            return False

    def fire(self, targetX, targetY, _type, _range):
        print "pulling the trigger"
        bearing = util.bearing(self.mapX, self.mapY, targetX, targetY)
        shot = Projectile(self, _type, self.mapX, self.mapY, targetX, targetY, bearing, _range)
        self.map.addEntity(shot, shot.mapX, shot.mapY)
        self.reloading = True
        self.coolDown = 0
        self.map.trigger('showReload', self, self)
        print shot
        return shot

    def fireCannon(self, x, y, _range):
        print "cannonballs"
        if not self.cannonballs:
            # TODO don't fire
            pass
        return self.fire(x, y, 'cannon', _range)

    def fireChain(self, x, y, range):
        print "chainshot"
        if not self.chainshot:
            # TODO don't fire
            pass
        return self.fire(x, y, 'chain', range)

    def updateCoolDown(self):
        if self.reloading:
            if self.coolDown >= config.ship['coolDown']:
                self.reloading = False
                self.coolDown = 0
                self.map.trigger('hideReload', self, self)
            self.coolDown += 1


class ShipPlacementError(Exception):
    pass

