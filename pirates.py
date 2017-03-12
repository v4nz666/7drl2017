from pygame import mixer

from RoguePy.libtcod import libtcod

__author__ = 'jripley'
from states import *
import config
from RoguePy.Game import Game


import RoguePy

RoguePy.setFps(config.fps)


game = Game("Pirates of Rogue Basin", config.layout['uiWidth'], config.layout['uiHeight'], False)
game.addState(SplashState('splash'))
game.addState(GenerateState('generate'))
game.addState(PlayState('play'))
game.addState(HighScoreState('highScore'))
game.addState(CreditsState('credits'))
game.addState(MainMenuState('mainMenu'))

game.run('mainMenu')

mixer.music.stop()
mixer.quit()
