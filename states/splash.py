__author__ = 'jripley'

import sys

from config import *
from RoguePy.Input import Keys
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.State import GameState
from sounds import *

class SplashState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()

    def beforeLoad(self):
        mixer.music.load(os.path.join(path, 'intro.wav'))
        mixer.music.play(-1)

    def setupView(self):
        titleString = 'Pirates of Rogue Basin'
        titleX = (layout['uiWidth'] - len(titleString)) / 2
        titleY = layout['uiHeight'] / 2 - 3
        title = Elements.Label(titleX, titleY, titleString) \
            .setDefaultForeground(Colors.dark_crimson)
        self.view.addElement(title)

        creditString = 'Jeff Ripley - 7DRL 2017'
        creditX = (layout['uiWidth'] - len(creditString)) / 2
        creditY = layout['uiHeight'] / 2 - 2
        credit = Elements.Label(creditX, creditY, creditString) \
            .setDefaultForeground(Colors.dark_grey)
        self.view.addElement(credit)

        pressKeyString = 'Press any key'
        pressKeyX = (layout['uiWidth'] - len(pressKeyString)) / 2
        pressKeyY = layout['uiHeight'] / 2
        pressKey = Elements.Label(pressKeyX, pressKeyY, pressKeyString) \
            .setDefaultForeground(Colors.darker_grey)
        self.view.addElement(pressKey)

    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.quit
            },
            'next': {
                'key': 'any',
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            }
        })

    @staticmethod
    def quit():
        mixer.music.stop()
        mixer.quit()
        print "Quitting"
        sys.exit()
