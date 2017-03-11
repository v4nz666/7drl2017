__author__ = 'jripley'

import sys
import config
from RoguePy.Input import Keys
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.State import GameState

class HighScoreState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()

    def beforeLoad(self):
        pass
    def setupView(self):
        self.frame = self.view.addElement(
            Elements.Frame(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], "Leaderboard")
        )




    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.quit
            }
        })

    @staticmethod
    def quit():
        print "Quitting"
        sys.exit()
