from RoguePy.libtcod import libtcod

rand = libtcod.random_get_instance()


def randint(mx, mn=0):
    return libtcod.random_get_int(rand, mn, mx)

def randfloat(mx, mn=0):
    return libtcod.random_get_float(rand, mn, mx)