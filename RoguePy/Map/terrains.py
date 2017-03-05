from Terrain import Terrain
from RoguePy.UI import Colors

EMPTY = Terrain(True, True, "Empty space")

WALL = Terrain(False, False, "Stone wall")\
  .setColors(Colors.light_grey, Colors.darkest_grey * 0.4)\
  .setChar('#')

FLOOR = Terrain(True, True, "Stone floor")\
  .setColors(Colors.dark_grey, Colors.darkest_grey * 0.4)\
  .setChar('.')