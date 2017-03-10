from RoguePy.libtcod import libtcod


class Entity(object):

    def __init__(self, map, x, y, name, ch, fg, canSee=False, viewRadius=0, isPlayer = False):
        c = map.getCell(x, y)
        if ( c.entity != None ):
            raise Exception("Entity already present in map cell (%d,%d)" % (x, y))
        self.map = map
        self.x = x
        self.y = y
        self.mapX = x
        self.mapY = y
        self.name = name
        self.ch = ch
        self.fg = fg
        self.canSee = canSee
        self.viewRadius = viewRadius
        self.isPlayer = isPlayer
        if self.canSee:
            self._initFovMap()
            self.calculateFovMap()

    def inSight(self, x, y):
        return libtcod.map_is_in_fov(self.fovMap, x, y)

    def _initFovMap(self):
        w, h = self.map.width, self.map.height
        self.fovMap = libtcod.map_new(w, h)
        for y in range(h):
            for x in range(w):
                c = self.map.getCell(x, y)
                if c:
                    libtcod.map_set_properties(self.fovMap, x, y, c.terrain.transparent, c.terrain.passable)

    def calculateFovMap(self):
        libtcod.map_compute_fov(
            self.fovMap, self.mapX, self.mapY, self.viewRadius, True, libtcod.FOV_SHADOW
        )

        for _y in range(-self.viewRadius, self.viewRadius + 1):
            for _x in range(-self.viewRadius, self.viewRadius + 1):
                if self.isPlayer:
                    x = self.mapX + _x
                    y = self.mapY + _y
                    c = self.map.getCell(x, y)
                    if c and self.inSight(x, y):
                        c.seen = True

    def updateFov(self):
        pass

    def tryMove(self, dx, dy):
        # Rest / skip check.
        if dx == 0 and dy == 0:
            return True

        # Adjacency check.
        if abs(dx) >  1 or abs(dy) > 1:
            return False

        dest = self.map.getCell(self.x + dx, self.y + dy)

        # Entity check.
        if dest.entity != None:
            self.map.trigger('entity_interact', self, dest.entity)
            return False

        # Terrain check.
        if not self.canEnter(dest):
            self.map.trigger('entity_collide', self, dest)
            return False

        # TODO: This should be a map call because (a) it's ugly, and (b) it makes assumptions about
        #   how map stores entities.
        self.map.getCell(self.x, self.y).entity = None
        self.x += dx
        self.y += dy
        self.map.getCell(self.x, self.y).entity = self
        return True

    def canEnter(self, cell):
        return cell.type == 'floor'
