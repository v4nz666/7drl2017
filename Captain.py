from Ship import Ship
from util import randint, getColor


class Captain(object):
    def __init__(self, ship=None):
        # TODO replace with name generation
        self.name = "Captain"
        self.morale = 50
        self.ship = ship
        self.skills = {
            'nav': randint(10),
            'gun': randint(10),
            'charisma': randint(10)
        }
        self.gold = 0
        self.lastCity = None

        self.setMoraleColor()

    def setMoraleColor(self):
        self.moraleColor = getColor(self.morale)

    def setCity(self, city):
        self.lastCity = city

    def setShip(self, ship):
        print "Setting ship with goods{}".format(ship.goods)
        self.ship = ship

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

        print "Gold[{}] cost[{}]".format(self.gold, cost)
        if self.gold < cost:
            return False

        ship = Ship(self.lastCity.map, shipType, self.lastCity.portX, self.lastCity.portY, True, stats)
        print "immediate goods {}".format(ship.goods)
        ship.calculateFovMap()

        if self.ship:
            print "selling goods {}".format(self.ship.goods)
            for item in self.ship.goods.keys():
                count = self.ship.goods[item]
                while count:
                    # If we can't take it on the new ship,
                    if self.ship.addGoods(item):
                        # we'll sell it
                        self.gold += self.lastCity.prices[item][1]
                        self.ship.takeGoods(item)
                        count -= 1
            self.sellShip()
        self.gold -= newShipValue
        print "new gold {}".format(self.gold)
        self.lastCity.removeShip(shipType, stats)

        self.setShip(ship)
        print "Bought [{}] ship with stats {}. Goods{}".format(shipType, stats, self.ship.goods)

        return True

    def moraleAdjust(self, val):
        self.morale += val
        if self.morale > 100:
            self.morale = 100
        if self.morale < 0:
            self.morale = 0
        self.setMoraleColor()

    def sellShip(self):
        value = Ship.getSellPrice(self.ship.stats)
        print "Selling ship for {}".format(value)
        self.gold += value
        print "Gold after sale {}".format(self.gold)
        self.lastCity.addShip(self.ship.name, self.ship.stats)
        self.ship.map.removeEntity(self.ship, self.ship.mapX, self.ship.mapY)
        self.ship = None

