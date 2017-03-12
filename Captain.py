import sys

from RoguePy.libtcod import libtcod

import config
import util
from Ship import Ship
from util import randint, getColor, getPirateName


class Captain(object):
    def __init__(self, navBase, gunBase, ship=None):
        self.name = getPirateName()
        self.morale = 50

        self.__opinion = 100
        self.attackingPlayer = False
        self.isPirate = False
        self.ship = ship
        self.rep = 0

        self.skills = {
            'nav': randint(navBase),
            'gun': randint(gunBase)
        }

        self.gold = 0
        self.lastCity = None
        self.atSea = False

        self.daysWithoutFood = 0
        self.daysAtSeaTotal = 0
        self.__daysAtSea = 0
        self.daysAtSea = 0
        
        self.__shotsFired = 0
        
        self.recalculateHeading = True
        self.sinceRecalc = 0

        self.destination = None
        self.path = None

        self.dead = False

        if ship:
            self.setShip(ship)

    @property
    def opinion(self):
        return self.__opinion
    @opinion.setter
    def opinion(self, val):
        self.__opinion = min(max(0, val), 100)
        if self.__opinion <= config.rep['threshold']:
            if not self.attackingPlayer and not self.isPirate:
                self.ship.map.trigger('repChanged', self, self)
                self.attackingPlayer = True


    def updateViewRadius(self):
        self.ship.viewRadius = min(max(self.skills['nav'], config.ship['minView']), config.ship['maxView'])
        self.ship.calculateFovMap()
    
    @property
    def shotsFired(self):
        return self.__shotsFired
    @shotsFired.setter
    def shotsFired(self, val):
        self.__shotsFired = val
        if not self.shotsFired % config.skill['gunShots']:
            if self.skills['gun'] < config.skill['max']:
                self.skills['gun'] += 1

    @property
    def daysAtSea(self):
        return self.__daysAtSea
    @daysAtSea.setter
    def daysAtSea(self, val):
        if not self.atSea:
            return
        
        diff = val - self.__daysAtSea
        self.__daysAtSea = val
        self.daysAtSeaTotal += diff

        if not self.daysAtSeaTotal % config.skill['navDays']:
            if self.skills['nav'] < config.skill['max']:
                self.skills['nav'] += 1
                self.updateViewRadius()

    def setDestination(self, destination):
        self.destination = destination
        self.path = util.getPath(self.ship.map)
        util.checkPath(self.ship.map, self.ship.mapX, self.ship.mapY, destination.portX, destination.portY, self.path)
        if not util.pathSize(self.path):
            self.destination = self.lastCity
            util.checkPath(self.ship.map, self.ship.mapX, self.ship.mapY, self.lastCity.portX, self.lastCity.portY, self.path)
            if not util.pathSize(self.path):
                self.dead = True
                return False
        return True

    def __str__(self):
        return "Captain {}".format(self.name)

    def returnToPort(self):

        if self.ship and self.morale < config.morale['awolThreshold']:
            count = randint(int(self.ship.crew * 0.75))
            self.ship.map.trigger('crew_left', self.ship, self.ship)
            self.ship.crew -= count

        increase = int(self.daysAtSea * config.morale['daysAtSeaReturn'])
        self.moraleAdjust(increase)

    def setCity(self, city):
        self.lastCity = city

    def setShip(self, ship):
        self.ship = ship
        self.ship.captain = self
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
        self.lastCity.removeShip(shipType, stats)

        self.setShip(ship)
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
        self.gold += value
        self.lastCity.addShip(self.ship.name, self.ship.stats)
        self.ship.map.removeEntity(self.ship, self.ship.mapX, self.ship.mapY)
        self.ship = None
        return value

