__author__ = 'jripley'
from states import *
import config
from RoguePy.Game import Game
import argparse


parser = argparse.ArgumentParser(description='Pirates of Rogue Basin')
parser.add_argument('--full', dest='fullScreen', action='store_true', help='run the game in fullscreen mode')

args = parser.parse_args()
print args
fullscreen = args.fullScreen

# Shenanigans to get RoguePy in the search path when it's the project root.
import sys
from config import *

import RoguePy

RoguePy.setFps(config.fps)


game = Game("Pirates of Rogue Basin", config.layout['uiWidth'], config.layout['uiHeight'], fullscreen)
game.addState(SplashState('splash'))
game.addState(GenerateState('generate'))
game.addState(PlayState('play'))
game.addState(HighScoreState('highScore'))
# game.addState(LoseState('lose'))

game.run('highScore')
