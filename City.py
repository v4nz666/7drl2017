import config
from RoguePy.Game import Entity
from util import randint, randfloat


class City(Entity):

    def __init__(self, map, x, y, name, ch, fg):
        super(City, self).__init__(map, x, y, name, ch, fg)
        self.shops = [
            'Dock',
            'General Store'
        ]

        self.prices = {}

        self.size = randint(1, 4)
        self.setShops()
        self.setGoods()

        self.crewAvailable = int(randfloat(.25, 2) * self.size)

    def __str__(self):
        return '{}[{}] at {}, {}\n  Shops: {}\n Port: {}, {}'.format(self.name, self.size, self.x, self.y, self.shops, self.portX, self.portY)

    def setShops(self):

        possibleShops = list(config.city['possibleShops'])

        count = self.size
        while count:
            i = randint(len(possibleShops) - 1)
            self.shops.append(possibleShops[i])
            del(possibleShops[i])
            count -= 1

    def setGoods(self):

        self.gold = randint(1000) * self.size,
        self.goods = {
            'food': randint(500) * self.size,
            'rum': randint(200) * self.size,
            'wood': randint(200) * self.size,
            'cloth': randint(200) * self.size,
            'coffee': randint(100) * self.size,
            'spice': randint(100) * self.size,
        }

    def setPrices(self):
        for item in ['food','rum','wood','cloth','coffee','spice']:
            self.prices[item] = self.calculateBuySellPrice(item)
        self.brothelRate = int(self.size * randfloat(0.8, 1.2) * config.brothel['baseRate'])
        self.brothelReturn = min(int(self.size * randfloat(0.8, 1.2) * config.brothel['baseReturn']), 100)
        print "Brothel Rate: {} Return: {}".format(self.brothelRate, self.brothelReturn)

    def getPrices(self, item):
        return self.prices[item]

    def getBuyPrice(self, item):
        return self.getPrices(item)[0]

    def getSellPrice(self, item):
        return self.getPrices(item)[1]

    def calculateBuySellPrice(self, item):
        count = self.goods[item]

        mul = 1.0
        if count < config.economy['lowThreshold']:
            mul = 1.5
        elif count <= config.economy['highThreshold']:
            mul = 0.75

        base = config.economy['basePrice'][item]
        rand = randfloat(0.9, 1.1)
        buyPrice = int(base * config.economy['buyMul'] * mul * rand)
        sellPrice = int(base * config.economy['sellMul'] * mul * rand)
        return buyPrice, sellPrice

    def getGoods(self):
        return self.goods

    def setPort(self, portX, portY):
        self.portX = portX
        self.portY = portY

