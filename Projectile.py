import util
from RoguePy.UI import Colors
from RoguePy.libtcod import libtcod
from RoguePy.Map import Entity
import config


class Projectile(Entity):
    def __init__(self, parent, type, x, y, tx, ty, heading, range, dmg):
        super(Projectile, self).__init__('projectile')
        self.ch = '*'
        self.heading = heading
        self.speed = config.projectile['speed']
        self.damage = dmg

        self.type = type

        if type == "cannon":
            clr = Colors.black
        else:
            clr = Colors.silver
        self.color = clr
        self.range = range

        self.distanceTravelled = 0
        self.distanceToTarget = int(util.dist(x, y, tx, ty))
        self.canSee = False

        self.parent = parent
        self.x = x
        self.y = y

    def __str__(self):
        return "Projectile[{},{}] spd [{}] hdg[{}]".format(self.x, self.y, self.speed, self.heading)

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

