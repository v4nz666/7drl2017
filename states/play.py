from util import randfloat, degToRad
from math import sin, cos
from Captain import Captain
from City import City
from RoguePy.Game import Map, Entity
from RoguePy.UI import Elements
from RoguePy.UI import Colors
from RoguePy.Input import Keys
from RoguePy.State import GameState
from RoguePy.UI import View
from RoguePy.libtcod import libtcod

import config
import sys

from Ship import Ship

__author__ = 'jripley'


class PlayState(GameState):
    def init(self):
        self.setupView()
        self.setupInputs()

        self.windSpeed = 5.0
        self.windDir = 180.0
        self.windEffectX = 0.0
        self.windEffectY = 0.0

        self.addHandler('fpsUpdate', 60, self.fpsUpdate)
        self.addHandler('windUpdate', config.fps * 2, self.windUpdate)
        self.addHandler('shipsUpdate', 1, self.shipsUpdate)

        self.disableHandler('shipsUpdate')

    def beforeLoad(self):
        self.addView(self.introModal)
        self.addHandler('intro', 1, self.doIntro)

    def shipsUpdate(self):
        self.playerUpdate()

    def playerUpdate(self):
        self.moveShip(self.player.ship)

    def moveShip(self, ship):
        if ship.anchored:
            return False
        dx = config.spf * cos(ship.heading * degToRad) * ship.speed * config.speedAdjust + self.windEffectX
        dy = config.spf * sin(ship.heading * degToRad) * ship.speed * config.speedAdjust + self.windEffectY

        oldX = ship.mapX
        oldY = ship.mapY
        ship.x += dx
        ship.y -= dy

        if ship.mapX < 0:
            ship.x = 0
        elif ship.mapX >= self.map.width:
            ship.x = self.map.width - 1
        if ship.mapY < 0:
            ship.y = 0
        elif ship.mapY >= self.map.height:
            ship.y = self.map.height - 1

        if ship.mapX == oldX and ship.mapY == oldY:
            return False

        destination = self.map.getCell(ship.mapX, ship.mapY)
        if destination and destination.type is not 'water':
            print "You're probably dead!"
            ship.x = oldX
            ship.y = oldY
            return False

        self.map.removeEntity(ship, oldX, oldY)
        self.map.addEntity(ship, ship.mapX, ship.mapY)
        self.mapElement.setDirty(True)
        ship.calculateFovMap()
        neighbours = self.map.getNeighbours(ship.mapX, ship.mapY)
        for nx, ny in neighbours:
            n = neighbours[nx, ny]
            if isinstance(n.entity, City):
                print "City! {},{}".format(nx, ny)
                print "Ship  {},{}".format(ship.mapX, ship.mapY)

        if ship.isPlayer:
            self.mapElement.center(ship.mapX, ship.mapY)
        return True

    def fpsUpdate(self):
        fps = libtcod.sys_get_fps()
        self.fpsLabel.setLabel('{}FPS'.format(fps))

    def windUpdate(self):

        self.windSpeed += randfloat(config.wind['speedJitter'], -config.wind['speedJitter'])
        maxSpd = config.wind['maxSpeed']
        if self.windSpeed < 0:
            self.windSpeed = 0
        if self.windSpeed > maxSpd:
            self.windSpeed = maxSpd

        if self.windSpeed <= maxSpd * 0.33:
            clr = Colors.green
        elif self.windSpeed <= maxSpd * 0.5:
            clr = Colors.dark_green
        elif self.windSpeed <= maxSpd * 0.666:
            clr = Colors.dark_yellow
        elif self.windSpeed <= maxSpd * 0.85:
            clr = Colors.dark_flame
        else:
            clr = Colors.red

        self.windLabel.setLabel(str(round(self.windSpeed, 2))).setDefaultForeground(clr)

        self.windDir += randfloat(config.wind['dirJitter'], -config.wind['dirJitter'])
        if self.windDir < 0:
            self.windDir += 360
        if self.windDir >= 360:
            self.windDir -= 360
        self.windDial.setVal(int(self.windDir))

        self.windEffectX = config.spf * cos(self.windDir * degToRad) * self.windSpeed * config.wind['impact']
        self.windEffectY = config.spf * sin(self.windDir * degToRad) * self.windSpeed * config.wind['impact']

    def updateAnchorUI(self):
        if self.player.ship.anchored:
            self.anchorLabel.bgOpacity = 1.0
            self.anchorLabel.setDefaultForeground(Colors.copper)
            self.anchorLabel.enable()
            self.infoPanel.setDirty(True)
        else:
            self.anchorLabel.bgOpacity = 0.0
            self.anchorLabel.setDefaultForeground(Colors.dark_grey)
            self.anchorLabel.disable()
            self.infoPanel.setDirty(True)

    def updateHeadingDial(self):
        if not self.player.ship:
            return
        self.headingDial.setVal(self.player.ship.heading)
        self.headingLabel.setLabel(str(self.player.ship.heading))

    def doIntro(self):
        majorCities = self.map.getMajorCities()
        menuItems = []
        for city in majorCities:
            menuItems.append({city.name: self.citySelected})

        modal = self.introModal
        menuHeight = min(len(majorCities), 5)
        self.introMenu = modal.addElement(Elements.Menu(1, modal.height - menuHeight - 1, modal.width - 2, menuHeight, menuItems))

        self.introModal.setKeyInputs({
            'moveUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': self.introMenu.selectUp
            },
            'moveUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': self.introMenu.selectUp
            },
            'moveDn': {
                'key': Keys.Down,
                'ch': 's',
                'fn': self.introMenu.selectDown
            },
            'moveDn2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': self.introMenu.selectDown
            },
            'selectCity': {
                'key': Keys.Enter,
                'ch': None,
                'fn': self.introMenu.selectFn
            },
            'selectCity2': {
                'key': Keys.NumPadEnter,
                'ch': None,
                'fn': self.introMenu.selectFn
            }
        })
        self.removeHandler('intro')

    def leavePort(self, city):
        pass

    def setMap(self, map):
        self.map = map
        self.mapElement = Elements.Map(0, 0, config.layout['uiWidth'] - self.infoPanel.width, config.layout['uiHeight'],
                                       self.map)
        self.mapElement.showFog = True

        self.view.addElement(self.mapElement)
        self.setFocus(self.mapElement)

        self.logMap = self.logFrame.addElement(
            Elements.Map(1, 1, self.logFrame.width - 2, self.logFrame.height - 2, self.map))
        self.logMap.isStatic = True
        self.logMap.showFog = True
        self.mapOverlay = self.logMap.addElement(Elements.Element(0, 0, self.logMap.width, self.logMap.height))
        self.mapOverlay.bgOpacity = 0
        self.mapOverlay.draw = self.drawOverlay

        self.cityLabel = None

    def drawOverlay(self):
        self.mapOverlay.setDirty(True)
        cursorX, cursorY = self.logMap.onScreen(self.mapX, self.mapY)
        libtcod.console_put_char_ex(
            self.mapOverlay.console, cursorX, cursorY, '+', Colors.chartreuse, Colors.white)

    def setupView(self):
        self.infoPanel = self.view.addElement(Elements.Frame(55, 0, 20, 36, "Info"))
        self.infoPanel.addElement(Elements.Label(1, 1, "Heading")).setDefaultForeground(Colors.flame)
        self.headingDial = self.infoPanel.addElement(Elements.Dial(1, 2)).setDefaultForeground(Colors.brass)
        self.headingLabel = self.infoPanel.addElement(Elements.Label(self.headingDial.x,
                                                                     self.headingDial.y + self.headingDial.height,
                                                                     "0.0   ")).setDefaultForeground(Colors.brass)

        self.infoPanel.addElement(Elements.Label(14, 1, "Wind")).setDefaultForeground(Colors.flame)
        self.windDial = self.infoPanel.addElement(Elements.Dial(14, 2)).setDefaultForeground(Colors.brass)
        self.windLabel = self.infoPanel.addElement(Elements.Label(self.windDial.x,
                                                                  self.windDial.y + self.windDial.height,
                                                                  "     "))
        self.anchorLabel = self.infoPanel.addElement(Elements.Label(6, 3, "<ANCHOR>"))\
            .setDefaultBackground(Colors.darker_red)

        self.infoPanel.addElement(Elements.Label(3, 9, "CAPTAIN")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 10, "Gold")).setDefaultForeground(Colors.gold)
        self.goldLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 7, 10, "      ")). \
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
        self.infoPanel.addElement(Elements.Label(1, 24, "Cannonball")).setDefaultForeground(Colors.darker_azure)
        self.foodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 24, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 25, "Chainshot")).setDefaultForeground(Colors.darker_azure)
        self.rumCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 25, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 28, "CARGO")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 29, "Food")).setDefaultForeground(Colors.darker_azure)
        self.foodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 29, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 30, "Rum")).setDefaultForeground(Colors.darker_azure)
        self.rumCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 30, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 31, "Wood")).setDefaultForeground(Colors.darker_azure)
        self.woodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 31, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 32, "Cloth")).setDefaultForeground(Colors.darker_azure)
        self.clothCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 32, "0".zfill(5))).\
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 33, "Coffee")).setDefaultForeground(Colors.darker_azure)
        self.coffeeCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 33, "0".zfill(5))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 34, "Spice")).setDefaultForeground(Colors.darker_azure)
        self.spiceCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 34, "0".zfill(5))). \
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
        self.fpsLabel = self.helpPanel.addElement(Elements.Label(2, self.helpPanel.height - 2, "000fps"))

        halfX = self.view.width / 2
        halfY = self.view.height / 2

        #### Captain's Log Modal
        modalX = halfX / 4 - 1
        modalY = halfY / 4
        modalW = halfX * 3 / 2 + 2
        modalH = halfY * 3 / 2

        self.logModal = View(modalW, modalH, modalX, modalY)

        logString = "CAPTAIN'S LOG"
        strX = modalW / 2 - len(logString) / 2
        self.logModal.addElement(Elements.Label(strX, 1, logString)).setDefaultForeground(Colors.gold)

        self.mapTab = self.logModal.addElement(Elements.Frame(1, 3, 7, 2, "(M)ap"))
        self.newsTab = self.logModal.addElement(Elements.Frame(9, 3, 8, 2, "(N)ews")).disable()

        self.logFrame = self.logModal.addElement(Elements.Frame(0, 4, self.logModal.width, self.logModal.height - 4))
        self.modalBackLabel = self.logModal.addElement(Elements.Label(3, modalH - 1, "TAB - Back"))

        frame = self.logFrame
        # logMap set in setMap
        self.logNews = frame.addElement(Elements.List(1, 1, frame.width - 2, frame.height - 2)).hide()

        #### Intro modal
        modalX = halfX / 2 - 1
        modalY = halfY / 2
        modalW = halfX
        modalH = halfY

        self.introModal = View(modalW, modalH, modalX, modalY)
        self.introModal.addElement(Elements.Frame(0, 0, modalW, modalH, "Welcome!"))
        introText =\
            "  Welcome to Rogue Basin. Home of great opportunity for a young captain like yourself. " +\
            "There has been a drastic increase in Pirate activity of late, and as such, the King " +\
            "has been handing out Letters of Marque to just about anyone who's willing to help rid " +\
            "the seas of the Pirate threat.\n\n" +\
            "  Never one to miss out on a chance for new adventures, you snatch up the chance, gather " +\
            "your life savings and head to the big city to find a ship."
        self.introModal.addElement(Elements.Text(1, 2, modalW - 2, 15, introText)). \
            setDefaultForeground(Colors.dark_green)

        pickACity =\
            "Please choose your starting Port"
        self.introModal.addElement(Elements.Text(1, modalH - 7, modalW - 2, 1, pickACity)). \
            setDefaultForeground(Colors.dark_red)

    def setupInputs(self):
        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.quit
            },
            'showLogModal': {
              'key': Keys.Tab,
              'ch': None,
              'fn': self.openLogModal
            },
            'headingCCW': {
                'key': Keys.NumPad4,
                'ch': "a",
                'fn': lambda:
                    self.player.ship and
                    self.headingAdjust(11.25)
            },
            'headingCCW2': {
                'key': Keys.Left,
                'ch': "A",
                'fn': lambda:
                    self.player.ship and
                    self.headingAdjust(11.25)
            },
            'headingCW': {
                'key': Keys.NumPad6,
                'ch': "d",
                'fn': lambda:
                    self.player.ship and
                    self.headingAdjust(-11.25)
            },
            'headingCW2': {
                'key': Keys.Right,
                'ch': "D",
                'fn': lambda:
                    self.player.ship and
                    self.headingAdjust(-11.25)
            },
            'toggleAnchor': {
                'key': Keys.Space,
                'ch': None,
                'fn': self.toggleAnchor

            },
            'sailsUp': {
                'key': Keys.NumPad8,
                'ch': "W",
                'fn': lambda:
                    self.player.ship and
                    self.player.ship.sailAdjust(1)
            },
            'sailsUp2': {
                'key': Keys.Up,
                'ch': "W",
                'fn': lambda:
                    self.player.ship and
                    self.player.ship.sailAdjust(1)
            },
            'sailsDn': {
                'key': Keys.NumPad2,
                'ch': "s",
                'fn': lambda:
                    self.player.ship and
                    self.player.ship.sailAdjust(-1)
            },
            'sailsDn2': {
                'key': Keys.Down,
                'ch': "S",
                'fn': lambda:
                    self.player.ship and
                    self.player.ship.sailAdjust(-1)
            },

        })

        self.logModal.setKeyInputs({
            'hideModal': {
                'key': Keys.Tab,
                'ch': None,
                'fn': lambda:
                    self.removeView() and self.enableGameHandlers()
            },
            'hideModal2': {
                'key': Keys.Escape,
                'ch': None,
                'fn': lambda:
                    self.removeView() and self.enableGameHandlers()
            },
            'showMap': {
                'key': None,
                'ch': 'm',
                'fn': self.showMap
            },
            'showNews': {
                'key': None,
                'ch': 'n',
                'fn': self.showNews
            },
        })

    def toggleAnchor(self):

        self.player.ship.toggleAnchor()
        print "Anchor toggled[{}]".format(self.player.ship.anchored)
        self.updateAnchorUI()

    def headingAdjust(self, val):
        if not self.player.ship:
            return
        self.player.ship.headingAdjust(val)
        self.updateHeadingDial()

    def showMap(self):
        if self.logMap.visible:
            return
        self.mapTab.enable()
        self.logMap.show()
        self.newsTab.disable()
        self.logNews.hide()

    def showNews(self):
        if self.logNews.visible:
            return
        self.mapTab.disable()
        self.logMap.hide()
        self.newsTab.enable()
        self.logNews.show()

    def openLogModal(self):
        self.disableHandler('shipsUpdate')
        self.addView(self.logModal)
        self.mapX, self.mapY = self.player.ship.mapX, self.player.ship.mapY
        self.logMap.center(self.mapX, self.mapY)

    def citySelected(self, index):

        cities = self.map.getMajorCities()

        startingCity = cities[index]
        print "Starting at ", startingCity
        # Close intro modal
        self.removeView()

        self.mapElement.center(startingCity.portX, startingCity.portY)

        self.logMap.setDirectionalInputHandler(self.moveMap)

        playerShip = Ship(self.map, 'Caravel', startingCity.portX, startingCity.portY, Colors.lighter_grey, isPlayer=True)
        # TODO Let the player pick from a few randomly generated captains
        self.player = Captain()
        self.player.setShip(playerShip)
        self.player.gold = 700
        self.mapElement.setPlayer(self.player)

        self.enableGameHandlers()

    def enableGameHandlers(self):
        # Enable our gameplay handlers
        self.enableHandler('windUpdate')
        self.enableHandler('shipsUpdate')

        self.updateAnchorUI()

    def clearCityLabel(self):
        if self.cityLabel is not None:
            self.logMap.removeElement(self.cityLabel)
            self.cityLabel = None

    def moveMap(self, dx, dy):

        self.clearCityLabel()

        newX = self.mapX + dx
        newY = self.mapY + dy
        if 0 <= newX < self.map.width:
            self.mapX = newX
        if 0 <= newY < self.map.height:
            self.mapY = newY

        self.logMap.center(self.mapX, self.mapY)

        cell = self.map.getCell(self.mapX, self.mapY)
        if cell and not cell.seen:
            return
        try:
            if isinstance(cell.entity, City):
                city = cell.entity
                cityLabelX = city.x - len(city.name) / 2
                cityLabelY = city.y + 1

                if cityLabelX < 0:
                    cityLabelX = 0
                if cityLabelX + len(city.name) >= self.map.width:
                    cityLabelX = self.map.width - len(city.name)
                if cityLabelY >= self.map.height - 1:
                    cityLabelY = self.map.height - 3
                cityLabelX, cityLabelY = self.logMap.onScreen(cityLabelX, cityLabelY)

                self.cityLabel = self.logMap.addElement(Elements.Label(cityLabelX, cityLabelY, city.name))
            else:
                self.cityLabel = None

        # TODO: Hack to deal with moving the cursor over the buggy section of the map
        #   (See https://github.com/v4nz666/7drl2017/issues/19)
        except AttributeError:
            print 'failed at {},{}'.format(self.mapX, self.mapY)

    @staticmethod
    def quit():
        print "Quitting"
        sys.exit()


# TODO: UTIL Stuff.. shouldn't be here
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
