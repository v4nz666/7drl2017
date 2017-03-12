__author__ = 'jripley'

import sys
import config
from RoguePy.Input import Keys
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.State import GameState
import util
from RoguePy.libtcod import libtcod
from sounds import *

class MainMenuState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()

    def beforeLoad(self):
        mixer.music.stop()
        mixer.music.load(os.path.join(path, 'intro.wav'))
        mixer.music.play(-1)

    def setupView(self):

        self.frame = self.view.addElement(
            Elements.Frame(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], "Main Menu")
        )
        
        width = config.layout['uiWidth'] - 4
        height = config.layout['uiHeight'] - 4;
        
        xOffset = width / 2 - 3
        yOffset = height / 2 - 2

        title = self.frame.addElement(Elements.Label(2, 2 * height / 5, "Pirates of Rogue Basin".center(width)))
        titleBars = self.frame.addElement(Elements.Label(2, 2 * height / 5, "------                        ------".center(width)))
        subtitle = self.frame.addElement(Elements.Label(2, 2 * height / 5 + 3, "Jeff Ripley - 7DRL 2017".center(width)))

        self.menu = self.frame.addElement(Elements.Menu(xOffset, 3 * height / 5, 11, 4))
        
        self.menu.setItems([
            {'   Play!   ': lambda x: self.manager.setNextState('generate')},
            {'  Credits  ': lambda x: self.manager.setNextState('credits')},
            {'Leaderboard': lambda x: self.manager.setNextState('highScore')},
            {'   Quit!   ': sys.exit}
        ])
        
        self.frame.setDefaultColors(Colors.lighter_sepia, Colors.darkest_sepia, True)
        self.frame.setDefaultForeground(Colors.gold)
        title.setDefaultForeground(Colors.lightest_sepia)

        titleBars.setDefaultForeground(Colors.gold).bgOpacity = 0.0
        subtitle.setDefaultForeground(Colors.darker_red)
        


    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'scrollUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': self.menu.selectUp
            },
            'scrollDown': {
                'key': Keys.Down,
                'ch': 's',
                'fn': self.menu.selectDown
            },
            'scrollUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': self.menu.selectUp
            },
            'scrollDown2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': self.menu.selectDown
            },
            'enter': {
                'key': Keys.Enter,
                'ch': None,
                'fn': self.menu.selectFn
            },
            'enter2': {
                'key': Keys.NumPadEnter,
                'ch': None,
                'fn': self.menu.selectFn
            }
        })

    # Fill a string of length 1 with str1, and st2, filling the space between with fillChar
    @staticmethod
    def fillSpace(width, str1, str2, fillChar):
        
        align = "<"
            
        length = width - len(str2)
            
        formatter = '{0:{fillChar}{align}' + str(length) + "}"
        return formatter.format(str1, fillChar=fillChar, align=align) + str2
