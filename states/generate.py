__author__ = 'jripley'

import random
from RoguePy.Game import Map, Entity
from RoguePy.UI import Elements
from RoguePy.UI import Colors
import terrains

import config
import sys
from RoguePy.Input import Keys
from RoguePy.State import GameState
from RoguePy.libtcod import libtcod


class GenerateState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()
        self.focusX = config.layout['uiWidth'] / 2
        self.focusY = config.layout['uiHeight'] / 2

    def beforeLoad(self):
        self.addHandler('gen', 1, self.generateWorld)

    def beforeUnload(self):
        pass

    def setupView(self):
        loadingText = "Generating"
        loadingX = (self.view.width - len(loadingText)) / 2
        loadingY = self.view.height / 2 - 3
        self.loadingLabel = self.view.addElement(Elements.Label(loadingX, loadingY, loadingText)) \
            .setDefaultForeground(Colors.dark_azure)

    def setupMapView(self):
        self.mapElement = Elements.Map(0, 0, config.layout['uiWidth'], config.layout['uiHeight'], self.map)
        self.view.addElement(self.mapElement)
        self.mapElement.center(self.focusX, self.focusY)

        self.mapElement.setDirectionalInputHandler(self.moveMap)
        self.setFocus(self.mapElement)

        keyFrame = Elements.Frame(config.layout['uiWidth'] / 4 - 2, 1, config.layout['uiWidth'] / 2 + 5, 3, "World Preview")
        self.mapElement.addElement(keyFrame).setDefaultColors(Colors.white, Colors.darker_grey)
        keysString = 'Spc - Play | R - Regenerate | Esc - Quit'
        keys = Elements.Label(1, 1, keysString) \
            .setDefaultForeground(Colors.gold)
        keys.bgOpacity = 0
        keyFrame.addElement(keys)

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
            },
            'regen': {
                'key': None,
                'ch': 'r',
                'fn': self.regenerate
            }
        })

    def regenerate(self):
        self.beforeUnload()
        self.beforeLoad()

    def moveMap(self, dx, dy):

        halfX = self.mapElement.width / 2
        halfY = self.mapElement.height / 2

        newX = self.focusX + dx
        newY = self.focusY + dy
        if newX >= halfX and newX < self.map.width - halfX:
            self.focusX = newX
        if newY >= halfY and newY < self.map.height - halfY:
            self.focusY = newY
        self.mapElement.center(self.focusX, self.focusY)

    def generateWorld(self):
        while True:
            w = config.world['width']
            h = config.world['height']

            hm = libtcod.heightmap_new(w, h)

            hills = 1024
            hillHeight = 15
            hillRad = 50
            libtcod.heightmap_clear(hm)

            for i in range(hills):
                height = config.randint(hillHeight)
                rad = config.randint(hillRad)

                hillX1 = config.randint(config.world['width'])
                hillY1 = config.randint(config.world['height'])

                hillX2 = config.randint(config.world['width'])
                hillY2 = config.randint(config.world['height'])

                if config.randint(10) < 3:
                    libtcod.heightmap_dig_hill(hm, hillX1, hillY1, height, rad)
                    libtcod.heightmap_dig_hill(hm, hillX2, hillY2, height, rad)
                else:
                    libtcod.heightmap_add_hill(hm, hillX1, hillY1, height, rad)
                    libtcod.heightmap_add_hill(hm, hillX2, hillY2, height, rad)
            libtcod.heightmap_rain_erosion(hm, 10000, 0.3, 0.2)
            libtcod.heightmap_normalize(hm, 0.0, 1024.0)

            thresholds = [
                {
                    'type': 'water',
                    'range': 0.333
                }, {
                    'type': 'grass',
                    'range': 0.666
                }, {
                    'type': 'mountain',
                    'range': 0.9
                }
            ]

            self.map = Map.FromHeightmap(hm, thresholds)

            libtcod.heightmap_delete(hm)

            if self.validMap():
                self.setupMapView()
                self.removeHandler('gen')
                print "Done..."
                return True
            else:
                print "invalid map. Retrying"


    def validMap(self):
        return True


    def play(self):
        self.manager.getState('play') \
            .setMap(self.map)
        self.manager.setNextState('play')
