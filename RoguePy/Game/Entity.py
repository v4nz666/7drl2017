
class Entity(object):

    def __init__(self, map, x, y, name, ch, fg):
        c = map.getCell(x, y)
        if ( c.entity != None ):
            raise Exception("Entity already present in map cell (%d,%d)" % (x, y))
        c.entity = self
        self.map = map
        self.x = x
        self.y = y
        self.name = name
        self.ch = ch
        self.fg = fg

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
