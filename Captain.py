from util import randint

class Captain(object):
    def __init__(self, ship):
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
