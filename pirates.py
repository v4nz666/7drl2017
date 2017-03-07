__author__ = 'jripley'
from states import *
import config
from RoguePy.Game import Game

# Shenanigans to get RoguePy in the search path when it's the project root.
import sys
from config import *

import RoguePy
from RoguePy.Input import Keys
from RoguePy.UI import Elements

RoguePy.setFps(config.fps)


game = Game("Pirates of Rogue Basin", config.layout['uiWidth'], config.layout['uiHeight'], False)
game.addState(SplashState('splash'))
game.addState(GenerateState('generate'))
game.addState(PlayState('play'))
# game.addState(WinState('win'))
# game.addState(LoseState('lose'))

game.run('splash')
