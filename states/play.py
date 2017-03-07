import util
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

    def beforeLoad(self):
        self.addView(self.introModal)
        self.addHandler('intro', 1, self.doIntro)

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
            }
        })

        self.logModal.setKeyInputs({
            'hideModal': {
                'key': Keys.Tab,
                'ch': None,
                'fn': self.removeView
            },
            'hideModal2': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.removeView
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
        self.addView(self.logModal)

    def citySelected(self, index):

        cities = self.map.getMajorCities()

        startingCity = cities[index]
        print "Starting at ", startingCity
        # Close intro modal
        self.removeView()

        self.mapElement.center(startingCity.portX, startingCity.portY)

        self.mapX = startingCity.portX
        self.mapY = startingCity.portY
        self.logMap.center(self.mapX, self.mapY)
        self.logMap.setDirectionalInputHandler(self.moveMap)

        playerShip = Ship(self.map, 'Caravel', startingCity.portX, startingCity.portY, Colors.magenta, isPlayer=True)
        # TODO Let the player pick from a few randomly generated captains
        self.player = Captain()
        self.player.setShip(playerShip)
        self.player.gold = 700
        self.mapElement.setPlayer(self.player)

    def clearCityLabel(self):
        if self.cityLabel is not None:
            self.logMap.removeElement(self.cityLabel)
            self.cityLabel = None

    def moveMap(self, dx, dy):

        self.clearCityLabel()

        print "Move ", dx, dy
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
