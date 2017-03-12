import util
from sounds import *
from RoguePy.Game import Map, Entity
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.Input import Keys
from RoguePy.State import GameState
from RoguePy.libtcod import libtcod

import config
import sys


__author__ = 'jripley'


class GenerateState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()
        self.focusX = config.layout['uiWidth'] / 2
        self.focusY = config.layout['uiHeight'] / 2

    def initCities(self):
        self.cities = [
            'Tortuga',
            'Clew Bay',
            'New Providence',
            'Barataria Bay',
            'Antigua',
            'Montserrat',
            'Port Royal',
            'Dominica',
            'Martinique',
            'Guadeloupe',
            'Santo Domingo',
            'Saba',
            'Saint Martin',
            'Sint Eustatius',
            'Curacao',
            'Bonaire',
            'Aruba',
            'St. Croix',
            'Tortola',
            'Anegada',
            'Virgin Gorda',
            'Anguilla',
            'Cap Francois',
            'Trafalgar',
            'San Juan de Ulua',
            'Miskito',
            'Honduras',
            'Port Antonio',
            'Morant Bay',
            'Ocho Rios',
            'Porto Cabezas',
            'Fort Wellington'
        ]

    def beforeLoad(self):
        self.initCities()
        self.addHandler('gen', 1, self.generateWorld)

    def beforeUnload(self):
        mixer.music.fadeout(500)
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
        keyFrame.bgOpacity = 0
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
                'fn': self.quit
            },
            'regen': {
                'key': None,
                'ch': 'r',
                'fn': self.regenerate
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

            hills = 512
            hillHeight = 10
            hillRad = 30
            libtcod.heightmap_clear(hm)

            for i in range(hills):
                height = util.randint(hillHeight)
                rad = util.randint(hillRad)

                hillX1 = util.randint(config.world['width'])
                hillY1 = util.randint(config.world['height'])

                hillX2 = util.randint(config.world['width'])
                hillY2 = util.randint(config.world['height'])

                if util.randint(10) < 3:
                    libtcod.heightmap_dig_hill(hm, hillX1, hillY1, height, rad)
                    libtcod.heightmap_dig_hill(hm, hillX2, hillY2, height, rad)
                else:
                    libtcod.heightmap_add_hill(hm, hillX1, hillY1, height, rad)
                    libtcod.heightmap_add_hill(hm, hillX2, hillY2, height, rad)
            libtcod.heightmap_rain_erosion(hm, 5000, 0.3, 0.2)
            libtcod.heightmap_normalize(hm, 0.0, 1024.0)

            
            thresholds = [
                {
                    'type': 'water',
                    'range': 0.333
                }, {
                    'type': 'grass',
                    'range': 0.5
                }, {
                    'type': 'tree',
                    'range': 0.666
                }, {
                    'type': 'mountain',
                    'range': 0.9
                }
            ]

            self.map = Map.FromHeightmap(hm, thresholds)
            libtcod.heightmap_delete(hm)

            if self.validMap():
                self.placeCities()

                if len(self.map.getMajorCities()) >= 4:
                    self.setupMapView()
                    self.removeHandler('gen')
                    print "Done..."
                    return True
                else:
                    print "Too few major cities. Retrying"
            else:
                print "invalid map. Retrying"

    def placeCities(self):

        cityCount = config.world['cityCount']
        if len(self.cities) < cityCount:
            self.initCities()

        while cityCount:

            x = util.randint(self.map.width - 1)
            y = util.randint(self.map.height - 1)

            c = self.map.getCell(x, y)
            if not c:
                continue
            if c.entity is not None or c.type != 'grass':
                continue

            elif not self.createCity(x, y):
                continue

            cityCount -= 1
        self.map.initCityNeighbours()

    def getOceanCorner(self):
        maxX = self.map.width - 1
        maxY = self.map.height - 1

        print "wh, xy", self.map.width, self.map.height, maxX, maxY

        c = self.map.getCell(0, 0)
        if c and c.type == "water" and util.checkPath(self.map, 0, 0, maxX, maxY):
            return 0, 0
        c = self.map.getCell(maxX, 0)
        if c and c.type == "water" and util.checkPath(self.map, maxX, 0, 0, maxY):
            return maxX, 0
        c = self.map.getCell(maxX, maxY)
        if c and c.type == "water" and util.checkPath(self.map, maxX, maxY, 0, 0):
            return maxX, maxY
        c = self.map.getCell(0, maxY)
        if c and c.type == "water" and util.checkPath(self.map, 0, maxY, maxX, 0):
            return 0, maxY

        # We failed :( but, we didn't try very hard, so it's fine
        return False

    def createCity(self, x, y):
        cell = self.map.getCell(x, y)

        if cell.entity:
            print "Entity present"
            return False

        waterNeighbours = self.map.getNeighboursOfType('water', x, y)
        if not len(waterNeighbours):
            return False

        grassNeighbours = self.map.getNeighboursOfType('grass', x, y)
        if len(grassNeighbours):
            for nx, ny in grassNeighbours:
                c = grassNeighbours[nx, ny]
                if c.entity:
                    print "Neighbouring tile has entity"
                    return False

        city = None
        for nx, ny in waterNeighbours:
            if (nx, ny) == (x, y):
                continue
            if not util.checkPath(self.map, nx, ny, self.testPoint[0], self.testPoint[1]):
                print "no path to ocean"
                continue
            else:
                city = self.map.addCity(x, y, nx, ny, self.getCityName())
                break
        if not city:
            print "Couldn't path to ocean"
            return False
        return True

    def validMap(self):
        self.testPoint = self.getOceanCorner()
        if self.testPoint is False:
            return False

        return True

    def getCityName(self):
        max = len(self.cities)
        i = util.randint(max - 1)
        name = self.cities[i]
        self.cities.remove(name)
        return name

    def play(self):
        self.manager.getState('play') \
            .setMap(self.map)
        self.manager.setNextState('play')

    @staticmethod
    def quit():
        mixer.music.stop()
        mixer.quit()
        print "Quitting"
        sys.exit()
