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
        self.setupView()
        self.setupInputs()

    def beforeLoad(self):
        pass
    def setupView(self):
        self.frame = self.view.addElement(
            Elements.Frame(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], "Leaderboard")
        )
        
        totalWidth = config.layout['uiWidth'] - 4
        scoreListWidth = totalWidth - 11
        height = config.layout['uiHeight'] - 4;


        # add score
        util.addScore(self.player.name, self.player.gold)
        
        # display Leaderboard
        
        headerText = self.fillSpace(scoreListWidth, "Name", "Score", " ")
        
        headers = self.frame.addElement(Elements.Label(2, 2, headerText))
        dateHeader = self.frame.addElement(Elements.Label(totalWidth - 2, 2, "Date"))
        
        
        # bar underneath headers
        bar = self.frame.addElement(Elements.Frame(1, 3, config.layout['uiWidth'] - 2, 2))
        bar.bgOpacity = 0;
        bar._chars = {k: ' ' for k in ['tl', 't', 'tr', 'r', 'br', 'b', 'bl', 'l']}
        bar._chars['t'] = libtcod.CHAR_HLINE
        
        
        scoresAndNames = util.getScores()
        
        scores = []
        dates = []
        
        for item in scoresAndNames:
            parts = item.split(":")
            
            line = self.fillSpace(scoreListWidth, parts[0], parts[1], ".")
            scores.append(line)
            
            dates.append(parts[2])
        
        
        self.scoreList = self.frame.addElement(Elements.List(2, 5, scoreListWidth, height - 3, scores))
        
        
        # add date column list
        self.dateList= self.frame.addElement(Elements.List(scoreListWidth + 4, 5, 10, height - 3, dates))
        
        
        
        self.frame.setDefaultColors(Colors.lightest_sepia, Colors.darker_sepia,True)
        self.frame.setDefaultForeground(Colors.gold)
        headers.setDefaultForeground(Colors.lightest_sepia)
        dateHeader.setDefaultForeground(Colors.lightest_sepia)
        bar.setDefaultForeground(Colors.gold)

    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.quit
            },
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
