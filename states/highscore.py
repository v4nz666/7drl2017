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
        self.setupInputs()

    def beforeLoad(self):
        if (self.player is not None):
            # add score
            util.addScore(self.player.name, self.player.gold)
        self.scoresAndNames = util.getScores()
        self.addHandler('drawScores', 1, self.drawScores)

    def beforeUnload(self):
        self.player = None

    def setupView(self):
        self.frame = self.view.addElement(
            Elements.Frame(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], "Leaderboard")
        )

        # display Leaderboard
        totalWidth = config.layout['uiWidth'] - 4
        self.scoreListWidth = totalWidth - 11
        scoreListHeight = config.layout['uiHeight'] - 4

        headerText = self.fillSpace(self.scoreListWidth, "Name", "Score", " ")

        self.frame.addElement(Elements.Label(2, 2, headerText)).setDefaultForeground(Colors.lightest_sepia)
        self.frame.addElement(Elements.Label(totalWidth - 2, 2, "Date"))\
            .setDefaultForeground(Colors.lightest_sepia)

        # bar underneath headers
        bar = self.frame.addElement(Elements.Frame(1, 3, config.layout['uiWidth'] - 2, 2))
        bar.bgOpacity = 0;
        bar._chars = {k: ' ' for k in ['tl', 't', 'tr', 'r', 'br', 'b', 'bl', 'l']}
        bar._chars['t'] = libtcod.CHAR_HLINE

        self.scoreList = self.frame.addElement(Elements.List(2, 5, self.scoreListWidth, scoreListHeight - 3))
        # add date column list
        self.dateList = self.frame.addElement(Elements.List(self.scoreListWidth + 4, 5, 10, scoreListHeight - 3))

        self.frame.setDefaultColors(Colors.lightest_sepia, Colors.darkest_sepia, True)
        self.frame.setDefaultForeground(Colors.gold)
        bar.setDefaultForeground(Colors.gold)

    def drawScores(self):
        scores = []
        dates = []
        
        for item in self.scoresAndNames:
            parts = item.split(":")
            line = self.fillSpace(self.scoreListWidth, parts[0], parts[1], ".")
            scores.append(line)
            dates.append(parts[2])

        self.scoreList.setItems(scores)
        self.dateList.setItems(dates)
        if self.player:
            self.drawPlayerScoreFrame()
        self.removeHandler('drawScores')

    def drawPlayerScoreFrame(self):
        width = config.layout['uiWidth']
        height = config.layout['uiHeight']

        frameWidth = 24
        frameHeight = 6

        self.playerScoreFrame = self.view.addElement(
            Elements.Frame(width / 2 - frameWidth / 2, height / 2 - frameHeight / 2, frameWidth, frameHeight, "Your Score"))

        self.playerScoreFrame.addElement(Elements.Label(1, 5, str("[Enter - OK]").center(frameWidth - 2)))

        self.playerScoreFrame.addElement(
            Elements.Text(1, 1, frameWidth - 2, 2, str(self.player.name).center(frameWidth - 2))) \
                .setDefaultForeground(Colors.sepia)
        self.playerScoreFrame.setDefaultColors(Colors.lightest_sepia, Colors.darker_sepia, True)

        self.playerScoreFrame.addElement(Elements.Label(1, 3, str(self.player.gold).center(frameWidth - 2))) \
            .setDefaultColors(Colors.gold, Colors.darker_sepia)

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
        self.frame.enable()

    def scrollUp(self):
        self.scoreList.scrollUp()
        self.dateList.scrollUp()

    def scrollDown(self):
        self.scoreList.scrollDown()
        self.dateList.scrollDown()

    @staticmethod
    def quit():
        sys.exit()
        
    # Fill a string of length 1 with str1, and st2, filling the space between with fillChar
    @staticmethod
    def fillSpace(width, str1, str2, fillChar):
        align = "<"
        length = width - len(str2)
        formatter = '{0:{fillChar}{align}' + str(length) + "}"
        return formatter.format(str1, fillChar=fillChar, align=align) + str2
