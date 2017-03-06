import util
from RoguePy.Game import Map, Entity
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.Input import Keys
from RoguePy.State import GameState
from RoguePy.libtcod import libtcod

import config
import sys

__author__ = 'jripley'


class PlayState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()
        self.focusX = config.layout['uiWidth'] / 2
        self.focusY = config.layout['uiHeight'] / 2

    def setMap(self, map):
        self.map = map

    def setupView(self):
        self.infoPanel = self.view.addElement(Elements.Frame(55, 0, 20, 36, "Info"))
        self.infoPanel.addElement(Elements.Label(1, 1, "Heading"))
        self.headingDial = self.infoPanel.addElement(Elements.Dial(1, 2))
        self.headingLabel = self.infoPanel.addElement(Elements.Label(self.headingDial.x + 1,
                                                                     self.headingDial.y + self.headingDial.height,
                                                                     "312"))

        self.infoPanel.addElement(Elements.Label(14, 1, "Wind"))
        self.windDial = self.infoPanel.addElement(Elements.Dial(14, 2))
        self.windLabel = self.infoPanel.addElement(Elements.Label(self.windDial.x + 1,
                                                                  self.windDial.y + self.windDial.height,
                                                                  "091"))

        self.infoPanel.addElement(Elements.Label(3, 9, "CAPTAIN")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 10, "Gold")).setDefaultForeground(Colors.gold)
        self.goldLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 7, 10, "000000")). \
            setDefaultForeground(Colors.gold)
        self.infoPanel.addElement(Elements.Label(1, 11, "Rep")).setDefaultForeground(Colors.darker_azure)
        self.repLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 11, "000")). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 12, "Skills")).setDefaultForeground(Colors.darker_flame)
        self.infoPanel.addElement(Elements.Label(1, 13, "Nav")).setDefaultForeground(Colors.darker_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 13, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 14, "Gun")).setDefaultForeground(Colors.darker_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 14, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 15, "Char")).setDefaultForeground(Colors.darker_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 15, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 17, "SHIP")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 18, "Crew(max)")).setDefaultForeground(Colors.darker_azure)
        self.crewCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 9, 18, "000")).\
            setDefaultForeground(Colors.azure)
        self.crewMaxLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 18, "({})".format(100))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 19, "Morale")).setDefaultForeground(Colors.darker_azure)
        self.moraleLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 19, "0".zfill(3))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 20, "Hull Dmg")).setDefaultForeground(Colors.darker_azure)
        self.hullDmgLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 20, "0".zfill(3))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 21, "Sail Dmg")).setDefaultForeground(Colors.darker_azure)
        self.SailDmgLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 21, "0".zfill(3))).\
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 23, "AMMO")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 24, "Canon Ball")).setDefaultForeground(Colors.darker_azure)
        self.foodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 24, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 25, "Grape Shot")).setDefaultForeground(Colors.darker_azure)
        self.rumCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 25, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 28, "CARGO")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 29, "Food")).setDefaultForeground(Colors.darker_azure)
        self.foodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 29, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 30, "Rum")).setDefaultForeground(Colors.darker_azure)
        self.rumCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 30, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 31, "Coffee")).setDefaultForeground(Colors.darker_azure)
        self.coffeeCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 31, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 32, "Spice")).setDefaultForeground(Colors.darker_azure)
        self.spiceCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 32, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)




        self.helpPanel = self.view.addElement(Elements.Frame(55, 35, 20, 15, "Help"))

        self.helpPanel.addElement(Elements.Label(1, 1, "A/D")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 1, "Heading L/R")).setDefaultForeground(Colors.azure)

        self.helpPanel.addElement(Elements.Label(1, 2, "W/S")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 2, "Sails Up/Dn")).setDefaultForeground(Colors.azure)

        self.helpPanel.addElement(Elements.Label(1, 4, "TAB")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 4, "Cptn's Log")).setDefaultForeground(Colors.azure)

        self.helpPanel.addElement(Elements.Label(1, 6, "SPC")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 6, "Anchor Up/Dn")).setDefaultForeground(Colors.azure)


    def setupMapView(self):
        self.mapElement = Elements.Map(0, 0, config.layout['uiWidth'] - self.infoPanel.width, config.layout['uiHeight'], self.map)
        self.view.addElement(self.mapElement)
        self.setFocus(self.mapElement)

    def setupInputs(self):

        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'next': {
                'key': Keys.Space,
                'ch': None,
                'fn': self.play
            },
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': sys.exit
            }
        })

        def leftClick(mouse):
            print "Left click"
            charSize = libtcod.sys_get_char_size()
            x, y = self.mapElement.fromScreen(mouse.x / charSize[0], mouse.y / charSize[1])

            if x == -1 or y == -1:
                return
            c = self.map.getCell(x, y)
            if c.entity:
                print c.entity

        self.view.setMouseInputs({
            'lClick': leftClick
        })

    def checkPath(self, x1, y1, x2, y2):
        path = libtcod.path_new_using_function(self.map.width, self.map.height, self.pathFunc)

        libtcod.path_compute(path, x1, y1, x2, y2)
        s = libtcod.path_size(path)
        libtcod.path_delete(path)
        if s:
            print "Got path, length", s
            return True
        else:
            return False

    def pathFunc(self, x1, y1, x2, y2, blech):
        c = self.map.getCell(x2, y2)
        if not c:
            return 0
        return int(c.terrain.passable)

    def play(self):
        self.manager.getState('play') \
            .setMap(self.map)
        self.manager.setNextState('play')
