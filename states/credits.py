__author__ = 'jripley'

import sys
import config
from RoguePy.Input import Keys
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.State import GameState
import util
from RoguePy.libtcod import libtcod

class CreditsState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()

    def beforeLoad(self):
        pass
    def setupView(self):
        self.frame = self.view.addElement(
            Elements.Frame(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], "Credits")
        )
        
        width = config.layout['uiWidth'] - 4
        height = config.layout['uiHeight'] - 4;
        
        numLines = 26
        yOffset = height / 2 - numLines / 2

        
        # display credits
        

        title = self.frame.addElement(Elements.Label(2, yOffset - 1, "------ Pirates of Rogue Basin ------".center(width)))
        subtitle = self.frame.addElement(Elements.Label(2, yOffset + 1, "Written by Jeff Ripley".center(width)))
        
        h1 = self.frame.addElement(Elements.Label(2, yOffset + 6, "Game Design".center(width)))
        
        self.frame.addElement(Elements.Label(2, yOffset + 8, "Jeff Ripley".center(width)))
        self.frame.addElement(Elements.Label(2, yOffset + 10, "Tara Mathers".center(width)))
            
            
            
        h2 = self.frame.addElement(Elements.Label(2, yOffset + 14, "Sounds & Artwork".center(width)))
        self.frame.addElement(Elements.Label(2, yOffset + 16, "Brad March".center(width)))
       
           
           
        h3 = self.frame.addElement(Elements.Label(2, yOffset + 20, "Play Testing".center(width)))
        self.frame.addElement(Elements.Label(2, yOffset + 22, "Ross Campbell".center(width)))
        self.frame.addElement(Elements.Label(2, yOffset + 24, "Simon Walker".center(width)))
        self.frame.addElement(Elements.Label(2, yOffset + 26, "Brad March".center(width)))

        
        
        self.frame.setDefaultColors(Colors.lightest_sepia, Colors.darkest_sepia,True)
        self.frame.setDefaultForeground(Colors.gold)
        
        title.setDefaultForeground(Colors.gold)
        h1.setDefaultForeground(Colors.gold)
        h2.setDefaultForeground(Colors.gold)
        h3.setDefaultForeground(Colors.gold)



    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'next': {
                'key': 'any',
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            }
        })

    @staticmethod
    def quit():
        print "Quitting"
        sys.exit()
        
    # Fill a string of length 1 with str1, and st2, filling the space between with fillChar
    @staticmethod
    def fillSpace(width, str1, str2, fillChar):
        
        align = "<"
            
        length = width - len(str2)
            
        formatter = '{0:{fillChar}{align}' + str(length) + "}"
        return formatter.format(str1, fillChar=fillChar, align=align) + str2
