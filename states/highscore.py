__author__ = 'jripley'

import sys
import config
from RoguePy.Input import Keys
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.State import GameState
import util
from RoguePy.libtcod import libtcod

class HighScoreState(GameState):
    def init(self):
        self.player = None
        self.setupView()
        self.addHandler('draw', 1, self.drawScreen)

    def beforeLoad(self):
        if (self.player is not None):
            # add score
            util.addScore(self.player.name, self.player.gold)
        self.scoresAndNames = util.getScores()
        
    
    def beforeUnload(self):
        self.player = None
    def setupView(self):
        
        self.frame = self.view.addElement(
            Elements.Frame(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], "Leaderboard")
        )
        
    def drawScreen(self):
           
        totalWidth = config.layout['uiWidth'] - 4
        scoreListWidth = totalWidth - 11
        height = config.layout['uiHeight'] - 4;
        
        # display Leaderboard
        
        headerText = self.fillSpace(scoreListWidth, "Name", "Score", " ")
        
        headers = self.frame.addElement(Elements.Label(2, 2, headerText))
        dateHeader = self.frame.addElement(Elements.Label(totalWidth - 2, 2, "Date"))
        
        
        # bar underneath headers
        bar = self.frame.addElement(Elements.Frame(1, 3, config.layout['uiWidth'] - 2, 2))
        bar.bgOpacity = 0;
        bar._chars = {k: ' ' for k in ['tl', 't', 'tr', 'r', 'br', 'b', 'bl', 'l']}
        bar._chars['t'] = libtcod.CHAR_HLINE
        
        scores = []
        dates = []
        
        for item in self.scoresAndNames:
            parts = item.split(":")
            
            line = self.fillSpace(scoreListWidth, parts[0], parts[1], ".")
            scores.append(line)
            
            dates.append(parts[2])
        
        
        self.scoreList = self.frame.addElement(Elements.List(2, 5, scoreListWidth, height - 3, scores))
        
        
        # add date column list
        self.dateList= self.frame.addElement(Elements.List(scoreListWidth + 4, 5, 10, height - 3, dates))
        
        self.frame.setDefaultColors(Colors.lightest_sepia, Colors.darkest_sepia,True)
        self.frame.setDefaultForeground(Colors.gold)
        headers.setDefaultForeground(Colors.lightest_sepia)
        dateHeader.setDefaultForeground(Colors.lightest_sepia)
        bar.setDefaultForeground(Colors.gold)
        
        
        # player score frame
        if (self.player is not None):
            self.drawPlayerScoreFrame()    
        
        self.removeHandler('draw')
        
        if (self.player is not None):
            self.frame.disable()
            self.playerScoreFrame.show()
        
        self.setupInputs()
        
    def drawPlayerScoreFrame(self):
        width = config.layout['uiWidth']
        height = config.layout['uiHeight']
        
        frameWidth = 20;
        frameHeight = 10;
        self.playerScoreFrame = self.view.addElement(
            Elements.Frame(width / 2 - frameWidth / 2, height / 2 - frameHeight / 2, frameWidth, frameHeight, "Your Score"))
        
        self.playerScoreFrame.addElement(Elements.Label(1, 4, str(500).center(frameWidth - 2)))
        
        self.playerScoreFrame.addElement(Elements.Label(1, 8, str("[Enter - OK]").center(frameWidth - 2)))
        self.playerScoreFrame.addElement(Elements.Label(1, 8, str("[Enter - OK]").center(frameWidth - 2)))

        self.playerScoreFrame.setDefaultColors(Colors.lightest_sepia, Colors.darker_sepia,True)
        self.setupInputs()
    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            
            'scrollUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': self.scrollUp
            },
            'scrollDown': {
                'key': Keys.Down,
                'ch': 's',
                'fn': self.scrollDown
            },
            'scrollUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': self.scrollUp
            },
            'scrollDown2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': self.scrollDown
            }
        })
            
        self.frame.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            },
            'quit1': {
                'key': Keys.Enter,
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            },
            'quit2': {
                'key': Keys.Space,
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            },
            'quit3': {
                'key': Keys.NumPadEnter,
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            },
            'quit4': {
                'key': Keys.BackSpace,
                'ch': None,
                'fn': lambda: self.manager.setNextState('mainMenu')
            }
        })
           
        if (self.player is not None):
            self.playerScoreFrame.setKeyInputs({

                'enter': {
                    'key': Keys.Enter,
                    'ch': None,
                    'fn': self.closeScoreFrame
                },
                'enter2': {
                    'key': Keys.NumPadEnter,
                    'ch': None,
                    'fn': self.closeScoreFrame
                }
            })
            
    def closeScoreFrame(self): 
        self.playerScoreFrame.hide()
        self.view.enable()

    def scrollUp(self):
        self.scoreList.scrollUp()
        self.dateList.scrollUp()

    def scrollDown(self):
        self.scoreList.scrollDown()
        self.dateList.scrollDown()

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
