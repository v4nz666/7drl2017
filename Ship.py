from RoguePy.Game import Entity
from shipTypes import shipTypes


class Ship(Entity):
    def __init__(self, map, type, x, y, color):
        self.name = type
        for attr, value in shipTypes[type].iteritems():
            setattr(self, attr, value)
        self.ch = '@'
        self.anchored = True
        self.hullDamage = 0
        self.sailDamage = 0
        self.heading = 0
        self.sails = 0

        super(Ship, self).__init__(map, x, y, self.name, self.ch, color)
