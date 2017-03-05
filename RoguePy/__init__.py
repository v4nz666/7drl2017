from libtcod import libtcod
import UI.UI as UI
import UI.View
from Core import *
from State import *
from Input import *
import Map.Map as Map
import Game
def setFps(fps):
  libtcod.sys_set_fps(fps)

def getFps():
  return libtcod.sys_get_fps()
