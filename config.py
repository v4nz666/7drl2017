from RoguePy.libtcod import libtcod

layout = {
    'uiWidth': 75,
    'uiHeight': 50
}

world = {
    'width': 255,
    'height': 255
}







### Random
rand = libtcod.random_get_instance()


def randint(mx, mn=0):
    return libtcod.random_get_int(rand, mn, mx)
