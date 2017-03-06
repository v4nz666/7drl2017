from RoguePy.Game import Entity
from util import randint


class City(Entity):

    def __init__(self, map, x, y, name, ch, fg):
        super(City, self).__init__(map, x, y, name, ch, fg)
        self.shops = [
            'Dock',
            'General Store'
        ]
        self.size = randint(1, 4)
        self.setShops()

    def __str__(self):
        return '{}[{}] at {}, {}\n  Shops: {}\n Port: {}, {}'.format(self.name, self.size, self.x, self.y, self.shops, self.portX, self.portY)

    def setShops(self):
        possibleShops = [
            'Tavern',
            'Gov\'s house',
            'Brothel',
            'Shipyard'
        ]
        count = self.size
        while count:
            i = randint(len(possibleShops) - 1)
            self.shops.append(possibleShops[i])
            del(possibleShops[i])
            count -= 1

    def setPort(self, portX, portY):
        self.portX = portX
        self.portY = portY

