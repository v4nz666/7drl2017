import sys

import config
from RoguePy.Game import Entity
from Ship import Ship
from shipTypes import shipTypes
from util import randint, randfloat


class City(Entity):

    def __init__(self, map, x, y, name, portX, portY, ch, fg):
        super(City, self).__init__(map, x, y, name, ch, fg, True, config.city['viewRadius'])
        self.shops = [
            'Dock',
            'General Store'
        ]

        self.portX = portX
        self.portY = portY

        self.prices = {}
        self.repairRate = 0
        self.brothelRate = 0
        self.brothelReturn = 0

        self.size = randint(1, 4)
        self.setShops()
        self.setGoods()
        self.setPrices()

        self.availableShips = []
        self.availableShipStats = []
        self.setAvailableShips()

        self.news = []
        self.neighbours = []

        self.crewAvailable = randint(20, 5) * self.size

    def __str__(self):
        return '{}[{}] at {}, {}\n  Shops: {}\n Port: {}, {}'.format(self.name, self.size, self.x, self.y, self.shops, self.portX, self.portY)

    def generateNews(self):
        if randfloat(1) < 0.5:
            item = self.shortage()
            type = "shortage"
            effect = "skyrocket"

        else:
            item = self.surplus()
            type = "surplus"
            effect = "plummet"
        news = "{} {} at {}. Prices {}!".format(item, type, self.name, effect)
        self.addNews(news)
        for n in self.neighbours:
            if randfloat(1) < config.news['propogateThreshold']:
                n.addNews(news)

    def addNews(self, newsItem):
        self.news.append(newsItem)

    def removeNews(self, index):
        self.news.pop(index)

    def shortage(self):
        goods = self.goods.keys()
        item = goods[randint(len(goods) - 1)]
        print "{} shortage at {}".format(item, self.name)
        print "old price {}".format(self.prices[item])
        quantity = randint(config.economy['scarceThreshold'])
        self.goods[item] = quantity
        self.prices[item] = self.calculateBuySellPrice(item)
        print "new price {}".format(self.prices[item])
        return item

    def surplus(self):
        goods = self.goods.keys()
        item = goods[randint(len(goods) - 1)]
        print "{} surplus at {}".format(item, self.name)
        print "old price {}".format(self.prices[item])
        quantity = randint(config.economy['surplusThreshold'], config.economy['highThreshold'])
        self.goods[item] = quantity
        self.prices[item] = self.calculateBuySellPrice(item)
        print "new price {}".format(self.prices[item])
        return item

    def hireCrewMember(self):
        if self.crewAvailable:
            self.crewAvailable -= 1
            return True
        return False

    def setShops(self):

        possibleShops = list(config.city['possibleShops'])

        count = self.size
        while count:
            i = randint(len(possibleShops) - 1)
            self.shops.append(possibleShops[i])
            del(possibleShops[i])
            count -= 1

    def setGoods(self):

        self.gold = randint(1000) * self.size
        self.goods = {
            'food': randint(config.economy['surplusThreshold']),
            'rum': randint(config.economy['surplusThreshold']),
            'wood': randint(config.economy['surplusThreshold']),
            'cloth': randint(config.economy['surplusThreshold']),
            'coffee': randint(config.economy['surplusThreshold']),
            'spice': randint(config.economy['surplusThreshold'])
        }

    def setPrices(self):

        for item in config.economy['goods']:
            self.prices[item] = self.calculateBuySellPrice(item)

        self.brothelRate = int(self.size * randfloat(0.8, 1.2) * config.brothel['baseRate'])
        self.brothelReturn = min(int(self.size * randfloat(0.8, 1.2) * config.brothel['baseReturn']), 100)

        self.repairRate = int(randfloat(0.8, 1.2) * config.shipyard['repairRate'])

        self.ammoRate = int(randfloat(0.8, 1.2) * config.shipyard['ammoRate'])
        self.hireRate = int(randfloat(0.8, 1.2) * config.tavern['hireRate'])


    def getPrices(self, item):
        return self.prices[item]

    def getBuyPrice(self, item):
        return self.getPrices(item)[0]

    def getSellPrice(self, item):
        return self.getPrices(item)[1]

    def calculateBuySellPrice(self, item):
        count = self.goods[item]
        mul = 1.0
        if count < config.economy['scarceThreshold']:
            mul = 2.5
        elif count < config.economy['lowThreshold']:
            mul = 1.5
        elif count >= config.economy['highThreshold']:
            mul = 0.75
        elif count >= config.economy['surplusThreshold']:
            mul = 0.5

        base = config.economy['basePrice'][item]
        rand = randfloat(0.9, 1.1)
        buyPrice = int(base * config.economy['buyMul'] * mul * rand)
        sellPrice = int(base * config.economy['sellMul'] * mul * rand)
        return buyPrice, sellPrice

    def getGoods(self):
        return self.goods

    def setAvailableShips(self):
        for x in range(int(self.size * randfloat(3))):
            self.addShip()

    def getAvailableShip(self, index):

        if len(self.availableShips):
            return self.availableShips[index].keys()[0], self.availableShips[index].values()[0]
        else:
            return False, False

    def addShip(self, shipType=None, shipStats=None):

        if shipType is None:
            shipType = shipTypes.keys()[randint(len(shipTypes) - 1)]
        stats = shipStats
        if shipStats is None:
            shipStats = shipTypes[shipType]
            stats = {}
            for k, v in shipStats.iteritems():
                stats[k] = v
            stats['hullDamage'] = randint(25)
            stats['sailDamage'] = randint(25)

        self.availableShips.append(
            {shipType: stats}
        )

    def removeShip(self, shipType, stats):

        for key in range(len(self.availableShips)):
            myType, myStats = self.getAvailableShip(key)
            if shipType == myType and stats == myStats:
                del self.availableShips[key]
                break

    def setPort(self, portX, portY):
        self.portX = portX
        self.portY = portY

