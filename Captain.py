import sys

from RoguePy.libtcod import libtcod

import config
import util
from Ship import Ship
from util import randint, getColor, getPirateName


class Captain(object):
    def __init__(self, ship=None):
        # TODO replace with name generation
        self.name = getPirateName()
        self.morale = 50
        self.rep = 0
        self.ship = ship
        self.skills = {
            'nav': randint(10),
            'gun': randint(10)
        }

        self.gold = 0
        self.lastCity = None
        self.atSea = False

        self.daysWithoutFood = 0
        self.daysAtSeaTotal = 0
        self.__daysAtSea = 0
        self.daysAtSea = 0

        self.recalculateHeading = True
        self.sinceRecalc = 0

        self.destination = None
        self.path = None

        self.dead = False

    def updateViewRadius(self):
        self.ship.viewRadius = min(max(self.skills['nav'], config.ship['minView']), config.ship['maxView'])
        print "new View radius {}".format(self.ship.viewRadius)
        self.ship.calculateFovMap()

    @property
    def daysAtSea(self):
        return self.__daysAtSea
    @daysAtSea.setter
    def daysAtSea(self, val):
        if not self.atSea:
            return
        if self.ship.isPlayer:

            print "setting days at sea to {}".format(val)

        diff = val - self.__daysAtSea
        self.__daysAtSea = val
        self.daysAtSeaTotal += diff

        if not self.daysAtSeaTotal % config.skill['navDays']:
            if self.skills['nav'] < config.skill['max']:
                self.skills['nav'] += 1
                self.updateViewRadius()
                print "Nav skill increase! isPlayer [{}]".format(self.ship.isPlayer)

    def setDestination(self, destination):
        self.destination = destination
        self.path = util.getPath(self.ship.map)
        util.checkPath(self.ship.map, self.ship.mapX, self.ship.mapY, destination.portX, destination.portY, self.path)
        if not util.pathSize(self.path):
            print "No path to destination [{}]. Setting back to home port[{}].".format(destination.name, self.lastCity.name)
            self.destination = self.lastCity
            util.checkPath(self.ship.map, self.ship.mapX, self.ship.mapY, self.lastCity.portX, self.lastCity.portY, self.path)
            if not util.pathSize(self.path):
                print "No path anywhere. {}".format(libtcod.path_is_empty(self.path))
                self.dead = True
                return False
        print "got a path! {}".format(libtcod.path_size(self.path))
        return True

    def __str__(self):
        return "Captain {}".format(self.name)

    def returnToPort(self):

        if self.ship and self.morale < config.morale['awolThreshold']:
            count = randint(int(self.ship.crew * 0.75))
            self.ship.map.trigger('crew_left', self.ship, self.ship)
            self.ship.crew -= count
            print "{} crew left".format(count)

        increase = int(self.daysAtSea * config.morale['daysAtSeaReturn'])
        print "Morale boosted by {}".format(increase)
        self.moraleAdjust(increase)

    def setCity(self, city):
        self.lastCity = city

    def setShip(self, ship):
        print "Setting ship with goods{}".format(ship.goods)
        self.ship = ship
        self.updateViewRadius()

    @property
    def morale(self):
        return self.__morale
    @morale.setter
    def morale(self, val):
        self.__morale = min(100, max(val, 0))

    def buyShip(self, shipType, stats):
        newShipValue = Ship.getBuyPrice(stats)
        cost = newShipValue
        if self.ship:
            cost -= Ship.getSellPrice(self.ship.stats)

        if self.gold < cost:
            return False

        ship = Ship(self.lastCity.map, shipType, self.lastCity.portX, self.lastCity.portY, True, stats)

        salePrice = 0
        goodsPrice = 0
        if self.ship:
            print "selling goods {}".format(self.ship.goods)
            for item in self.ship.goods.keys():
                count = self.ship.goods[item]
                while count:
                    count -= 1
                    self.ship.takeGoods(item)
                    # If we can't take it on the new ship,
                    if not ship.addGoods(item):
                        # we'll sell it
                        goodsPrice += self.lastCity.prices[item][1]
                        self.gold += self.lastCity.prices[item][1]
            salePrice = self.sellShip()
        self.gold -= newShipValue
        print "new gold {}".format(self.gold)
        self.lastCity.removeShip(shipType, stats)

        self.setShip(ship)
        print "Bought [{}] ship with stats {}. Goods{}".format(shipType, stats, self.ship.goods)

        return salePrice, goodsPrice

    def moraleAdjust(self, val):
        old = self.morale
        self.morale += val
        if self.morale > 100:
            self.morale = 100
        if self.morale < 0:
            self.morale = 0
        return old != self.morale

    def sellShip(self):
        value = Ship.getSellPrice(self.ship.stats)
        print "Selling ship for {}".format(value)
        self.gold += value
        print "Gold after sale {}".format(self.gold)
        self.lastCity.addShip(self.ship.name, self.ship.stats)
        self.ship.map.removeEntity(self.ship, self.ship.mapX, self.ship.mapY)
        self.ship = None
        return value

