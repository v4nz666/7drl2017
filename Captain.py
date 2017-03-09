from util import randint


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

    def setShip(self, ship):
        self.ship = ship
        self.inSight = ship.inSight

    @property
    def morale(self):
        return self.__morale
    @morale.setter
    def morale(self, val):
        self.__morale = min(100, max(val, 0))


