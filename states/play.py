from shipTypes import shipTypes
from util import randfloat, degToRad, randint, getColor
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
        self.currentCity = None

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
        self.manager.updateUi(self)
        self.addView(self.introModal)
        self.addHandler('intro', 1, self.doIntro)

    def shipsUpdate(self):
        self.playerUpdate()

    def playerUpdate(self):
        if self.player.ship:
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
            self.anchorLabel.setDefaultForeground(Colors.brass)
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

    def enterCity(self, player, city):
        if player.ship:
            self.map.removeEntity(player.ship, player.ship.mapX, player.ship.mapY)
        self.currentCity = city
        player.setCity(city)
        self.addView(self.cityModal)

        city.setPrices()
        self.hideShops()
        self.disableShops()
        self.cityShowShop('generalStore')

        self.shipyardMenu.selected = 0
        self.storeMenu.selected = 0

        self.updateCityUI()
        print 'PORT {},{}'.format(city.portX, city.portY)

    def castOff(self, ship):
        if not self.player.ship:
            return False
        if self.player.ship.crew < self.player.ship.stats['minCrew']:
            print "Not enough crew to sail!"
            return False

        self.removeView()
        ship.anchored = True
        ship.heading = 0.0
        ship.sails = 0
        x, y = self.currentCity.portX, self.currentCity.portY
        ship.x = x
        ship.y = y
        print "Casting off to {},{}".format(x, y)
        self.map.addEntity(ship, x, y)
        self.currentCity = None


    def hideShops(self):
        for shop in config.city['possibleShops']:
            elementName = "{}Frame".format(shop)
            element = getattr(self, elementName)
            if shop not in self.currentCity.shops:
                element.hide()
            else:
                element.show()

    def disableShops(self):
        self.generalStoreFrame.disable()
        self.tavernFrame.disable()
        self.shipyardFrame.disable()

    def updateCityUI(self):
        city = self.currentCity
        self.cityFrame.setTitle('Welcome to {}!'.format(city.name))
        self.updateStoreItems()
        self.updateBrothelValues()
        self.updateTavernUI()
        self.updateShipyardUI()
        if not self.player.ship:
            self.dockFrame.disable()
        else:
            self.dockFrame.enable()

    def updateShipyardUI(self):
        # Repairs
        rateStr = "${}/{}".format(self.currentCity.repairRate, config.shipyard['repairReturn'])
        self.repairRateVal.setLabel(rateStr)
        if self.player.ship:
            hullDamage = self.player.ship.stats['hullDamage']
            sailDamage = self.player.ship.stats['sailDamage']
            hullColor = getColor(hullDamage)
            sailColor = getColor(sailDamage)
            self.repairHullCurrent.setLabel(str(hullDamage)).setDefaultForeground(hullColor)
            self.repairSailCurrent.setLabel(str(sailDamage)).setDefaultForeground(sailColor)

            if not self.player.ship.goods['wood']:
                self.notEnoughWood.setDefaultForeground(Colors.darker_red)
            else:
                self.notEnoughWood.setDefaultForeground(Colors.darker_green)
            if not self.player.ship.goods['cloth']:
                self.notEnoughCloth.setDefaultForeground(Colors.darker_red)
            else:
                self.notEnoughCloth.setDefaultForeground(Colors.darker_green)
        else:
            self.repairHullCurrent.setLabel('n/a').setDefaultForeground(Colors.darker_sepia)
            self.repairSailCurrent.setLabel('n/a').setDefaultForeground(Colors.darker_sepia)

        # Ammo
        self.ammoPriceLabel.setLabel("${}/{}" .format(self.currentCity.ammoRate, config.shipyard['ammoBuyCount']))
        if not self.player.ship:
            balls = "n/a"
            chain = "n/a"
        else:
            balls = str(self.player.ship.cannonballs)
            chain = str(self.player.ship.chainshot)
        print "balls, chain {}, {}".format(balls, chain)
        self.cannonballOnShip.setLabel(balls)
        self.chainshotOnShip.setLabel(chain)

        # Buy sell ships
        self.shipyardMenu.setItems(self.currentCity.availableShips)
        self.updateShipStats()
        

    def updateBrothelValues(self):
        c = self.currentCity
        if self.player.ship:
            crew = self.player.ship.crew
        else:
            crew = 0
        totalCrew = crew + 1
        self.brothelRateVal.setLabel(str(c.brothelRate))
        self.brothelCrewVal.setLabel(str("{}(+1)".format(crew)))
        self.brothelCost = c.brothelRate * (totalCrew)
        self.brothelCostVal.setLabel(str(self.brothelCost))
        self.brothelGoldVal.setLabel(str(self.player.gold))
        self.brothelMoraleVal.setLabel(str(self.player.morale))

    def updateStoreItems(self):

        cityGoods = self.currentCity.getGoods()
        self.storeTownGold.setLabel(str(self.currentCity.gold).zfill(5))
        self.storeTownFood.setLabel(str(cityGoods['food']).zfill(4))
        self.storeTownRum.setLabel(str(cityGoods['rum']).zfill(3))
        self.storeTownWood.setLabel(str(cityGoods['wood']).zfill(3))
        self.storeTownCloth.setLabel(str(cityGoods['cloth']).zfill(3))
        self.storeTownCoffee.setLabel(str(cityGoods['coffee']).zfill(3))
        self.storeTownSpice.setLabel(str(cityGoods['spice']).zfill(3))

        self.storeShipGold.setLabel(str(self.player.gold).zfill(5))

        if self.player.ship:
            shipGoods = self.player.ship.goods
            print "Ship goods {}".format(shipGoods)
            self.storeShipFood.setLabel(str(shipGoods['food']).zfill(4))
            self.storeShipRum.setLabel(str(shipGoods['rum']).zfill(3))
            self.storeShipWood.setLabel(str(shipGoods['wood']).zfill(3))
            self.storeShipCloth.setLabel(str(shipGoods['cloth']).zfill(3))
            self.storeShipCoffee.setLabel(str(shipGoods['coffee']).zfill(3))
            self.storeShipSpice.setLabel(str(shipGoods['spice']).zfill(3))

            inHold = self.player.ship.inHold
            shipSize = self.player.ship.stats['size']
        else:
            self.storeShipFood.setLabel(str(0).zfill(3))
            self.storeShipRum.setLabel(str(0).zfill(3))
            self.storeShipWood.setLabel(str(0).zfill(3))
            self.storeShipCloth.setLabel(str(0).zfill(3))
            self.storeShipCoffee.setLabel(str(0).zfill(3))
            self.storeShipSpice.setLabel(str(0).zfill(3))

            inHold = 0
            shipSize = 0
        self.inHoldVal.setLabel(str(inHold))
        self.inHoldTotal.setLabel(str(shipSize))

        self.updateBuySellPrices()

    def updateBuySellPrices(self):
        selectedItem = [
            'food',
            'rum',
            'wood',
            'cloth',
            'coffee',
            'spice'
        ][self.storeMenu.selected]

        buy, sell = self.currentCity.getPrices(selectedItem)

        self.buyPrice.setLabel(str(buy))
        self.sellPrice.setLabel(str(sell))



    def encounterShip(self, captain):
        pass

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

        self.map.on('enterCity', self.enterCity)
        self.map.on('encounterShip', self.encounterShip)

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
                                                                     "0.0   ")).setDefaultForeground(Colors.gold)

        self.infoPanel.addElement(Elements.Label(14, 1, "Wind")).setDefaultForeground(Colors.flame)
        self.windDial = self.infoPanel.addElement(Elements.Dial(14, 2)).setDefaultForeground(Colors.brass)
        self.windLabel = self.infoPanel.addElement(Elements.Label(self.windDial.x,
                                                                  self.windDial.y + self.windDial.height,
                                                                  "     "))
        self.anchorLabel = self.infoPanel.addElement(Elements.Label(6, 6, "<ANCHOR>")) \
            .setDefaultBackground(Colors.darker_red)

        self.infoPanel.addElement(Elements.Label(7, 8, "<SAIL>")).setDefaultForeground(Colors.brass)
        self.sailSlider = self.infoPanel.addElement(Elements.Slider(4, 9, 12, 0, config.maxSails)). \
            setDefaultForeground(Colors.brass)

        self.infoPanel.addElement(Elements.Label(3, 10, "CAPTAIN")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 11, "Gold")).setDefaultForeground(Colors.gold)
        self.goldLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 7, 11, "      ")). \
            setDefaultForeground(Colors.gold)
        self.infoPanel.addElement(Elements.Label(1, 12, "Rep")).setDefaultForeground(Colors.lighter_azure)
        self.repLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 12, "000")). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 13, "Skills")).setDefaultForeground(Colors.darker_flame)
        self.infoPanel.addElement(Elements.Label(1, 14, "Nav")).setDefaultForeground(Colors.lighter_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 14, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 15, "Gun")).setDefaultForeground(Colors.lighter_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 15, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 16, "Char")).setDefaultForeground(Colors.lighter_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 16, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 18, "SHIP")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 19, "Crew(max)")).setDefaultForeground(Colors.lighter_azure)
        self.crewCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 9, 19, "000")). \
            setDefaultForeground(Colors.azure)
        self.crewMaxLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 19, "({})".format(100))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 20, "Morale")).setDefaultForeground(Colors.lighter_azure)
        self.moraleLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 20, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 21, "Hull Dmg")).setDefaultForeground(Colors.lighter_azure)
        self.hullDmgLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 21, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 22, "Sail Dmg")).setDefaultForeground(Colors.lighter_azure)
        self.SailDmgLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 22, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 24, "AMMO")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 25, "Cannonball")).setDefaultForeground(Colors.lighter_azure)
        self.foodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 25, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 26, "Chainshot")).setDefaultForeground(Colors.lighter_azure)
        self.rumCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 26, "0".zfill(3))). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(3, 28, "CARGO")).setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(1, 29, "Food")).setDefaultForeground(Colors.lighter_azure)
        self.foodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 29, "0".zfill(5))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 30, "Rum")).setDefaultForeground(Colors.lighter_azure)
        self.rumCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 30, "0".zfill(5))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 31, "Wood")).setDefaultForeground(Colors.lighter_azure)
        self.woodCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 31, "0".zfill(5))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 32, "Cloth")).setDefaultForeground(Colors.lighter_azure)
        self.clothCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 32, "0".zfill(5))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 33, "Coffee")).setDefaultForeground(Colors.lighter_azure)
        self.coffeeCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 6, 33, "0".zfill(5))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 34, "Spice")).setDefaultForeground(Colors.lighter_azure)
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


        #### City Modal
        self.cityModal = View(modalW + 2, modalH + 2, modalX + 1, modalY - 1)
        self.cityFrame = self.cityModal.addElement(Elements.Frame(0, 0, modalW + 2, modalH + 2, "Welcome!"))
        self.generalStoreFrame = self.cityModal.addElement(Elements.Frame(1, 1, 28, 16, 'GE(N)ERAL STORE'))
        self.tavernFrame = self.cityModal.addElement(Elements.Frame(1, 17, 28, 11, '(T)AVERN'))
        self.dockFrame = self.cityModal.addElement(Elements.Frame(1, 28, 14, 10, '(D)OCK'))
        self.gossipFrame = self.cityModal.addElement(Elements.Frame(15, 28, 14, 10, '(G)OSSIP'))
        self.shipyardFrame = self.cityModal.addElement(Elements.Frame(29, 1, 29, 27, 'SHIP (Y)ARD'))
        self.brothelFrame = self.cityModal.addElement(Elements.Frame(29, 28, 29, 10, '(B)ROTHEL'))

        ### General Store
        self.generalStoreFrame.addElement(Elements.Label(2, 1, "on ship"))
        self.generalStoreFrame.addElement(Elements.Label(19, 1, "in town"))
        self.storeShipGold = self.generalStoreFrame.addElement(
            Elements.Label(1, 2, "12345"))
        self.storeShipFood = self.generalStoreFrame.addElement(
            Elements.Label(1, 3, "1234"))
        self.storeShipRum = self.generalStoreFrame.addElement(
            Elements.Label(1, 4, "123"))
        self.storeShipWood = self.generalStoreFrame.addElement(
            Elements.Label(1, 5, "123"))
        self.storeShipCloth = self.generalStoreFrame.addElement(
            Elements.Label(1, 6, "123"))
        self.storeShipCoffee = self.generalStoreFrame.addElement(
            Elements.Label(1, 7, "123"))
        self.storeShipSpice = self.generalStoreFrame.addElement(
            Elements.Label(1, 8, "123"))

        self.storeTownGold = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 6, 2, "12345"))
        self.storeTownFood = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 5, 3, "1234"))
        self.storeTownRum = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 4, 4, "123"))
        self.storeTownWood = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 4, 5, "123"))
        self.storeTownCloth = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 4, 6, "123"))
        self.storeTownCoffee = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 4, 7, "123"))
        self.storeTownSpice = self.generalStoreFrame.addElement(
            Elements.Label(self.generalStoreFrame.width - 4, 8, "123"))

        menuItems = [
            {'Food': lambda: None},
            {'Rum': lambda: None},
            {'Wood': lambda: None},
            {'Cloth': lambda: None},
            {'Coffee': lambda: None},
            {'Spice': lambda: None},
        ]

        self.storeMenu = self.generalStoreFrame.addElement(
            Elements.Menu(11, 3, 6, 6, menuItems))
        self.storeGoldLabel = self.generalStoreFrame.addElement(Elements.Label(11, 2, "Gold"))
        self.buyPriceFrame = self.generalStoreFrame.addElement(Elements.Frame(1, 9, 7, 3, "Buy"))
        buyDollar = self.buyPriceFrame.addElement(Elements.Label(1, 1, "$"))
        self.buyPrice = self.buyPriceFrame.addElement(Elements.Label(2, 1, "1000"))
        self.holdFrame = self.generalStoreFrame.addElement(Elements.Frame(8, 9, 11, 3, "Hold/max"))
        self.inHoldVal = self.holdFrame.addElement(Elements.Label(1, 1, "000"))
        holdSlash = self.holdFrame.addElement(Elements.Label(5, 1, '/'))
        self.inHoldTotal = self.holdFrame.addElement(Elements.Label(7, 1, "750"))

        self.sellPriceFrame = self.generalStoreFrame.addElement(Elements.Frame(19, 9, 7, 3, "Sell"))
        sellDollar = self.sellPriceFrame.addElement(Elements.Label(1, 1, "$"))
        self.sellPrice = self.sellPriceFrame.addElement(Elements.Label(2, 1, "1000"))

        salesFinal = self.generalStoreFrame.addElement(Elements.Label(6, 12, "All sales final!"))
        self.generalStoreFrame.addElement(Elements.Label(5, 13, "Up/Dn-Select Goods"))
        self.generalStoreFrame.addElement(Elements.Label(6, 14, "Lft/Rgt-Buy/Sell"))

        ### Shipyard
        # Repairs
        self.repairFrame = self.shipyardFrame.addElement(Elements.Frame(1, 1, 13, 8, 'REPAIRS'))
        self.repairHullLabel = self.repairFrame.addElement(Elements.Label(1, 2, "(H)ULL"))
        self.notEnoughWood = self.repairFrame.addElement(Elements.Label(8, 2, "wood"))
        self.repairRateVal = self.repairFrame.addElement(Elements.Label(3, 6, "      "))

        self.repairHullTotal = self.repairFrame.addElement(Elements.Label(6, 3, "/ 100"))
        self.repairHullCurrent = self.repairFrame.addElement(Elements.Label(2, 3, "000"))
        self.repairSailLabel = self.repairFrame.addElement(Elements.Label(1, 4, "(S)AIL"))
        self.notEnoughCloth = self.repairFrame.addElement(Elements.Label(7, 4, "cloth"))
        self.repairSailTotal = self.repairFrame.addElement(Elements.Label(6, 5, "/ 100"))
        self.repairSailCurrent = self.repairFrame.addElement(Elements.Label(2, 5, "000"))
        # Ammo
        self.ammoFrame = self.shipyardFrame.addElement(Elements.Frame(14, 1, 14, 8, 'AMMO'))
        self.ammoPriceLabel = self.ammoFrame.addElement(Elements.Label(3, 6, "$20/10"))
        self.cannonballLabel = self.ammoFrame.addElement(Elements.Label(1, 2, "C(a)nnonball"))
        self.cbOnShipLabel = self.ammoFrame.addElement(Elements.Label(1, 3, "on ship"))
        self.cannonballOnShip = self.ammoFrame.addElement(Elements.Label(10, 3, "   "))
        self.chainshotLabel = self.ammoFrame.addElement(Elements.Label(1, 4, "Cha(i)nshot"))
        self.csOnShipLabel = self.ammoFrame.addElement(Elements.Label(1, 5, "on ship"))
        self.chainshotOnShip = self.ammoFrame.addElement(Elements.Label(10, 5, "   "))
        # Ship sales
        self.shipSaleFrame = self.shipyardFrame.addElement(Elements.Frame(1, 9, 27, 17, 'SHIPS for SALE'))
        self.shipSaleHelp = self.shipSaleFrame.addElement(Elements.Label(1, self.shipSaleFrame.height - 1,
                                                                         "Up/Dn-Select | Enter buys"))
        self.shipyardMenu = self.shipSaleFrame.addElement(Elements.Menu(1, 2, 12, 13))
        self.shipyardMenu.setWrap(False)
        self.shipSpecFrame = self.shipSaleFrame.addElement(Elements.Frame(13, 2, 13, 13, "Ship Specs"))
        self.shipSpecs = self.shipSpecFrame.addElement(Elements.Dict(1, 2, 11, 8))
        self.damageLabel = self.shipSpecFrame.addElement(Elements.Label(4, 9, "Damage"))
        self.damageSpecs = self.shipSpecFrame.addElement(Elements.Dict(1, 10, 11, 2)).setItems({
            'hull': 85,
            'sail': 12
        })

        ### Brothel
        brothelText = "Treat the crew to a wild night. Expensive, but great for morale!"
        self.brothelText = self.brothelFrame.addElement(Elements.Text(3, 1, self.brothelFrame.width - 4, 3, brothelText))
        self.brothelRateLabel = self.brothelFrame.addElement(Elements.Label(7, 4, "Rate"))
        self.brothelRateVal = self.brothelFrame.addElement(Elements.Label(17, 4, "20"))
        self.brothelCrewLabel = self.brothelFrame.addElement(Elements.Label(7, 5, "Crew"))
        self.brothelCrewVal = self.brothelFrame.addElement(Elements.Label(17, 5, "120(+1)"))
        self.brothelCostLabel = self.brothelFrame.addElement(Elements.Label(7, 6, "Cost"))
        self.brothelCostVal = self.brothelFrame.addElement(Elements.Label(17, 6, "24000"))
        self.brothelGoldLabel = self.brothelFrame.addElement(Elements.Label(7, 7, "Gold"))
        self.brothelGoldVal = self.brothelFrame.addElement(Elements.Label(17, 7, "2553"))
        self.brothelMoraleLabel = self.brothelFrame.addElement(Elements.Label(7, 8, "Morale"))
        self.brothelMoraleVal = self.brothelFrame.addElement(Elements.Label(17, 8, "100"))

        ### Tavern
        tavernText = "You are greeted by a toothless bartender"
        self.tavernText = self.tavernFrame.addElement(Elements.Text(1, 1, 15, 3, tavernText))
        tavernQuote = '"Wha d\'ya want?'
        self.tavernQuote = self.tavernFrame.addElement(Elements.Label(1, 5, tavernQuote))
        self.buyARoundLabel = self.tavernFrame.addElement(Elements.Label(1, 7, "Buy a (R)ound"))
        self.hireCrewLabel = self.tavernFrame.addElement(Elements.Label(1, 8, "(H)ire Sailors"))
        self.tavernFrame.addElement(Elements.Label(18, 1, "on ship"))
        self.tavernFrame.addElement(Elements.Label(18, 8, "in town"))
        self.tavernCrewLabel = self.tavernFrame.addElement(Elements.Label(16, 9, "Crew"))
        self.tavernCrewAvailable = self.tavernFrame.addElement(Elements.Label(24, 9, "000"))

        self.tavernStats = self.tavernFrame.addElement(Elements.Dict(16, 2, 11, 5))

        ### Dock
        dockText = "Set sail for the open sea. Make sure you have enough food and rum for the journey!"
        self.dockText = self.dockFrame.addElement(
            Elements.Text(1, 1, self.dockFrame.width - 2, self.dockFrame.height - 2, dockText))

        ### Gossip
        gossipText = "Learn about profitable goods and pirates in the area."
        self.gossipText = self.gossipFrame.addElement(Elements.Text(1, 2, self.gossipFrame.width - 2, 7, gossipText))
        self.gossipRepLabel = self.gossipFrame.addElement(Elements.Label(1, 8, "Rep: "))
        self.gossipRepVal = self.gossipFrame.addElement(Elements.Label(11, 8, "55"))

        # City colors
        self.cityModal.setDefaultColors(Colors.sepia, Colors.darkest_sepia, True)
        self.cityModal.bgOpacity = 0.4

        self.generalStoreFrame.setDefaultForeground(Colors.lightest_sepia)
        self.tavernFrame.setDefaultForeground(Colors.lightest_sepia)
        self.brothelFrame.setDefaultForeground(Colors.lightest_sepia)
        self.shipyardFrame.setDefaultForeground(Colors.lightest_sepia)
        self.gossipFrame.setDefaultForeground(Colors.lightest_sepia)
        self.dockFrame.setDefaultForeground(Colors.lightest_sepia)

        # Store colors
        self.storeShipGold.setDefaultForeground(Colors.lighter_sepia)
        self.storeShipFood.setDefaultForeground(Colors.lighter_sepia)
        self.storeShipRum.setDefaultForeground(Colors.lighter_sepia)
        self.storeShipWood.setDefaultForeground(Colors.lighter_sepia)
        self.storeShipCloth.setDefaultForeground(Colors.lighter_sepia)
        self.storeShipCoffee.setDefaultForeground(Colors.lighter_sepia)
        self.storeShipSpice.setDefaultForeground(Colors.lighter_sepia)
        self.storeGoldLabel.setDefaultForeground(Colors.gold)
        self.storeTownGold.setDefaultForeground(Colors.lighter_sepia)
        self.storeTownFood.setDefaultForeground(Colors.lighter_sepia)
        self.storeTownRum.setDefaultForeground(Colors.lighter_sepia)
        self.storeTownWood.setDefaultForeground(Colors.lighter_sepia)
        self.storeTownCloth.setDefaultForeground(Colors.lighter_sepia)
        self.storeTownCoffee.setDefaultForeground(Colors.lighter_sepia)
        self.storeTownSpice.setDefaultForeground(Colors.lighter_sepia)
        self.buyPrice.setDefaultForeground(Colors.gold)
        self.sellPrice.setDefaultForeground(Colors.gold)

        self.inHoldVal.setDefaultForeground(Colors.lighter_sepia)
        # holdSlash.setDefaultForeground(Colors.lighter_sepia)
        self.inHoldTotal.setDefaultForeground(Colors.lighter_sepia)
        buyDollar.setDefaultForeground(Colors.gold)
        sellDollar.setDefaultForeground(Colors.gold)
        salesFinal.setDefaultForeground(Colors.darker_red)


        # Shipyard colors
        self.shipSpecFrame.setDefaultForeground(Colors.lighter_sepia, True)
        self.shipSaleHelp.setDefaultForeground(Colors.dark_sepia)
        self.shipyardMenu.setDefaultForeground(Colors.lighter_sepia)
        self.damageLabel.setDefaultForeground(Colors.darker_red)
        self.damageSpecs.setDefaultForeground(Colors.red)

        self.repairHullTotal.setDefaultForeground(Colors.lighter_sepia)
        self.repairSailTotal.setDefaultForeground(Colors.lighter_sepia)
        self.repairRateVal.setDefaultForeground(Colors.gold)
        self.repairHullCurrent.setDefaultForeground(Colors.darker_green)
        self.repairSailCurrent.setDefaultForeground(Colors.dark_red)
        self.notEnoughWood.setDefaultForeground(Colors.darker_red)
        self.notEnoughCloth.setDefaultForeground(Colors.darker_red)

        self.ammoPriceLabel.setDefaultForeground(Colors.gold)
        self.cannonballLabel.setDefaultForeground(Colors.lighter_sepia)
        self.chainshotLabel.setDefaultForeground(Colors.lighter_sepia)
        self.cbOnShipLabel.setDefaultForeground(Colors.dark_sepia)
        self.csOnShipLabel.setDefaultForeground(Colors.dark_sepia)
        self.cannonballOnShip.setDefaultForeground(Colors.brass)
        self.chainshotOnShip.setDefaultForeground(Colors.brass)

        # Tavern Colors
        self.buyARoundLabel.setDefaultForeground(Colors.lighter_sepia)
        self.hireCrewLabel.setDefaultForeground(Colors.lighter_sepia)
        self.tavernStats.setDefaultForeground(Colors.lighter_sepia)
        self.tavernCrewAvailable.setDefaultForeground(Colors.lighter_sepia)
        self.tavernCrewLabel.setDefaultForeground(Colors.lighter_sepia)
        # Brothel colors
        self.brothelText.setDefaultForeground(Colors.lightest_sepia)
        self.brothelRateVal.setDefaultForeground(Colors.gold)
        self.brothelCostVal.setDefaultForeground(Colors.gold)
        self.brothelGoldVal.setDefaultForeground(Colors.gold)

        #Gossip colors
        self.gossipText.setDefaultForeground(Colors.lightest_sepia)
        self.gossipRepVal.setDefaultForeground(Colors.lighter_sepia)

        # Dock colors
        self.dockText.setDefaultForeground(Colors.lightest_sepia)
        ## Intro modal
        modalX = halfX / 2 - 1
        modalY = halfY / 2
        modalW = halfX
        modalH = halfY

        self.introModal = View(modalW, modalH, modalX, modalY)
        self.introModal.addElement(Elements.Frame(0, 0, modalW, modalH, "Welcome!"))
        introText = \
            "  Welcome to Rogue Basin. Home of great opportunity for a young captain like yourself. " + \
            "There has been a drastic increase in Pirate activity of late, and as such, the King " + \
            "has been handing out Letters of Marque to just about anyone who's willing to help rid " + \
            "the seas of the Pirate threat.\n\n" + \
            "  Never one to miss out on a chance for new adventures, you snatch up the chance, gather " + \
            "your life savings and head to the big city to find a ship."
        self.introModal.addElement(Elements.Text(1, 2, modalW - 2, 15, introText)). \
            setDefaultForeground(Colors.dark_green)

        pickACity = \
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
                self.adjustSails(1)

            },
            'sailsUp2': {
                'key': Keys.Up,
                'ch': "W",
                'fn': lambda:
                self.player.ship and
                self.adjustSails(1)
            },
            'sailsDn': {
                'key': Keys.NumPad2,
                'ch': "s",
                'fn': lambda:
                self.player.ship and
                self.adjustSails(-1)
            },
            'sailsDn2': {
                'key': Keys.Down,
                'ch': "S",
                'fn': lambda:
                self.player.ship and
                self.adjustSails(-1)
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

        self.cityModal.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.quit
            },
            'castOff': {
                'key': None,
                'ch': 'd',
                'fn': lambda:
                    self.castOff(self.player.ship)
            },
            'castOff2': {
                'key': None,
                'ch': 'D',
                'fn': lambda:
                    self.castOff(self.player.ship)
            },
            'brothel': {
                'key': None,
                'ch': 'b',
                'fn': self.brothel
            },
            'brothel2': {
                'key': None,
                'ch': 'B',
                'fn': self.brothel
            },
            'showTavern': {
                'key': None,
                'ch': 't',
                'fn': lambda:
                    self.cityShowShop('tavern')
            },
            'showTavern2': {
                'key': None,
                'ch': 'T',
                'fn': lambda:
                    self.cityShowShop('tavern')
            },
            'showShipyard': {
                'key': None,
                'ch': 'y',
                'fn': lambda:
                    self.cityShowShop('shipyard')
            },
            'showShipyard2': {
                'key': None,
                'ch': 'Y',
                'fn': lambda:
                    self.cityShowShop('shipyard')
            },
            'showStore': {
                'key': None,
                'ch': 'n',
                'fn': lambda:
                self.cityShowShop('generalStore')
            },
            'showStore2': {
                'key': None,
                'ch': 'N',
                'fn': lambda:
                self.cityShowShop('generalStore')
            },
        })

        self.storeMenu.setKeyInputs({
            'menuUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': lambda: self.storeMenu.selectUp() and
                      self.updateBuySellPrices()
            },
            'menuUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': lambda: self.storeMenu.selectUp() and
                      self.updateBuySellPrices()
            },
            'menuDn': {
                'key': Keys.Down,
                'ch': 's',
                'fn': lambda: self.storeMenu.selectDown() and
                      self.updateBuySellPrices()
            },
            'menuDn2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': lambda: self.storeMenu.selectDown() and
                      self.updateBuySellPrices()
            },
            'buy': {
                'key': Keys.Left,
                'ch': 'a',
                'fn': lambda:
                    self.buyGoods(self.storeMenu.selected)
            },
            'buy2': {
                'key': Keys.NumPad4,
                'ch': 'A',
                'fn': lambda:
                    self.buyGoods(self.storeMenu.selected)
            },
            'sell': {
                'key': Keys.Right,
                'ch': 'd',
                'fn': lambda:
                    self.sellStuff(self.storeMenu.selected)
            },
            'sell2': {
                'key': Keys.NumPad6,
                'ch': 'D',
                'fn': lambda:
                    self.sellStuff(self.storeMenu.selected)
            },
        })
        self.shipyardMenu.setKeyInputs({
            'menuUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': lambda: self.shipyardMenu.selectUp() and
                              self.updateShipStats()
            },
            'menuUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': lambda: self.shipyardMenu.selectUp() and
                              self.updateShipStats()
            },
            'menuDn': {
                'key': Keys.Down,
                'ch': 's',
                'fn': lambda: self.shipyardMenu.selectDown() and
                              self.updateShipStats()
            },
            'menuDn2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': lambda: self.shipyardMenu.selectDown() and
                              self.updateShipStats()
            },
            'buyShip': {
                'key': Keys.Enter,
                'ch': None,
                'fn': self.buyShip

            },
            'buyShip2': {
                'key': Keys.NumPadEnter,
                'ch': None,
                'fn': self.buyShip
            },
            'fixHull': {
                'key': None,
                'ch': 'h',
                'fn': self.repairHull
            },
            'fixHull2': {
                'key': None,
                'ch': 'H',
                'fn': self.repairHull
            },
            'fixSails': {
                'key': None,
                'ch': 's',
                'fn': self.repairSails

            },
            'fixSails2': {
                'key': None,
                'ch': 'S',
                'fn': self.repairSails
            },
            'buyCannon': {
                'key': None,
                'ch': 'a',
                'fn': self.buyCannon

            },
            'buyCannon2': {
                'key': None,
                'ch': 'A',
                'fn': self.buyCannon

            },
            'buyChain': {
                'key': None,
                'ch': 'i',
                'fn': self.buyChain
            },
            'buyChain2': {
                'key': None,
                'ch': 'I',
                'fn': self.buyChain
            }

        })


        self.tavernFrame.setKeyInputs({
            'hire': {
                'key': None,
                'ch': 'h',
                'fn': self.hireCrew
            },
            'hire2': {
                'key': None,
                'ch': 'H',
                'fn': self.hireCrew
            },
            'buyRound': {
                'key': None,
                'ch': 'a',
                'fn': self.buyRound

            },
            'buyRound2': {
                'key': None,
                'ch': 'S',
                'fn': self.buyRound
            }
        })

    def hireCrew(self):
        if not self.player.ship or self.player.ship.crew >= self.player.ship.stats['maxCrew']:
            return False

        rate = self.currentCity.hireRate
        if self.player.gold >= rate and self.currentCity.hireCrewMember():
            self.player.ship.crew += 1
            self.updateCityUI()
            return True
        else:
            return False


    def buyRound(self):
        if not self.player.ship:
            crew = 0
        else:
            crew = self.player.ship.crew

        rate = (crew + 1)
        if self.player.gold >= rate:
            self.player.moraleAdjust(config.tavern['drinkMorale'])
            self.updateCityUI()
            return True
        else:
            return False

    def buyCannon(self):
        if not self.player.ship or not self.player.ship.addCannonballs(config.shipyard['ammoBuyCount']):
            print "Couldn't buy"
            return False
        print "bought balls"
        self.player.gold -= self.currentCity.ammoRate
        self.updateCityUI()

    def buyChain(self):
        if not self.player.ship or not self.player.ship.addChainshot(config.shipyard['ammoBuyCount']):
            print "couldn't buy"
            return False
        print "bought chain"
        self.player.gold -= self.currentCity.ammoRate
        self.updateCityUI()


    def repairHull(self):
        if not self.player.ship:
            return False
        cost = self.currentCity.repairRate
        if self.player.gold < cost:
            return False

        if not self.player.ship.takeGoods('wood'):
            return False

        if self.player.ship.repairHull():
            self.player.gold -= cost
            self.updateCityUI()

    def repairSails(self):
        if not self.player.ship:
            return False
        cost = self.currentCity.repairRate
        if self.player.gold < cost:
            return False

        if not self.player.ship.takeGoods('cloth'):
            return False

        if self.player.ship.repairSails():
            self.player.gold -= cost
            self.updateCityUI()

    def updateShipStats(self):
        if not len(self.currentCity.availableShips):
            return
        shipType, shipStats = self.currentCity.getAvailableShip(self.shipyardMenu.selected)
        stats = {}
        if shipStats:
            self.damageSpecs.setItems({
                'hull': shipStats['hullDamage'],
                'sail': shipStats['sailDamage']
            })
            for k in shipStats.keys():
                if k not in ['hullDamage', 'sailDamage', 'color']:
                    stats[k] = shipStats[k]
                if k == "price":
                    stats[k] = Ship.getBuyPrice(shipStats)
            self.shipSpecs.setItems(stats)

    def buyShip(self):
        shipType, stats = self.currentCity.getAvailableShip(self.shipyardMenu.selected)
        if self.player.buyShip(shipType, stats):
            self.shipyardMenu.selected = 0
            self.updateCityUI()


    def buyGoods(self, index):
        if not self.player.ship:
            return

        itemName = self.getItemByIndex(index)
        price = self.currentCity.getBuyPrice(itemName)

        if self.player.gold < price:
            return
        if self.currentCity.goods[itemName] < 1:
            return
        if not self.player.ship.addGoods(itemName):
            return

        self.currentCity.goods[itemName] -= 1
        self.player.gold -= price
        self.updateCityUI()

    def sellStuff(self, index):
        if not self.player.ship:
            return

        itemName = self.getItemByIndex(index)
        price = self.currentCity.getSellPrice(itemName)

        if self.currentCity.gold < price:
            return
        if not self.player.ship.takeGoods(itemName):
            return
        self.currentCity.goods[itemName] += 1
        self.player.gold += price
        self.currentCity.gold -= price
        self.updateCityUI()

    @staticmethod
    def getItemByIndex(index):
        return['food', 'rum', 'wood', 'cloth', 'coffee', 'spice'][index]

    def cityShowShop(self, name):
        self.disableShops()
        element = getattr(self, '{}Frame'.format(name))
        element.enable()

    def brothel(self):
        cost = self.currentCity.brothelRate * (self.player.ship.crew + 1)
        if self.player.gold >= cost and self.player.morale < 100:
            self.player.morale += self.currentCity.brothelReturn
            self.player.gold -= cost
        self.updateCityUI()

    def updateTavernUI(self):
        minCrew = "n/a"
        maxCrew = "n/a"
        crew = "n/a"
        if self.player.ship:
            minCrew = self.player.ship.stats['minCrew']
            maxCrew = self.player.ship.stats['maxCrew']
            crew = self.player.ship.crew

        tavernStats = {
            'Morale': self.player.morale,
            'MinCrew': minCrew,
            'MaxCrew': maxCrew,
            'Crew': crew,
            'Gold': self.player.gold
        }

        self.tavernCrewAvailable.setLabel(str(self.currentCity.crewAvailable))

        self.tavernStats.setItems(tavernStats)


    def adjustSails(self, val):
        self.player.ship.sailAdjust(val)
        self.sailSlider.val = self.player.ship.sails


    def toggleAnchor(self):
        ship = self.player.ship
        ship.toggleAnchor()
        self.updateAnchorUI()

        if ship.anchored:
            neighbours = self.map.getNeighbours(ship.mapX, ship.mapY)
            cityMenu = []
            cities = []
            for x, y in neighbours:
                c = neighbours[x, y]
                if isinstance(c.entity, City):
                    city = c.entity
                    cities.append(city)
                    label = "{} ({},{})".format(city.name, city.x, city.y)
                    cityMenu.append({
                        label:
                            lambda i: self.removeView() and self.enterCity(self.player, cities[i])
                    })
            # if len(cities) == 1:
            #     key = cities.keys()[0]
            #     self.enterCity(self.player, cities.pop(key))
            if len(cityMenu):
                self.citySelection(cityMenu)

    def citySelection(self, cityMenu):
        title = "Choose from the following cities:"

        cityMenu.append({
            'Keep sailing': self.removeView
        })

        modalX = (self.mapElement.width / 2 - len(title) / 2) - 1
        modalY = self.mapElement.height / 2 - 3
        modalW = len(title) + 2
        modalH = 6
        modal = View(modalW, modalH, modalX, modalY)
        self.addView(modal)

        modal.addElement(Elements.Frame(0, 0, modalW, modalH, title))
        menu = modal.addElement(Elements.Menu(1, 1, modalW - 2, modalH - 2, cityMenu))
        menu.setWrap(False)
        modal.setDefaultColors(Colors.lighter_sepia, Colors.darker_sepia, True)
        modal.setKeyInputs({
            'moveUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': menu.selectUp
            },
            'moveUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': menu.selectUp
            },
            'moveDn': {
                'key': Keys.Down,
                'ch': 's',
                'fn': menu.selectDown
            },
            'moveDn2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': menu.selectDown
            },
            'selectCity': {
                'key': Keys.Enter,
                'ch': None,
                'fn': menu.selectFn
            },
            'selectCity2': {
                'key': Keys.NumPadEnter,
                'ch': None,
                'fn': menu.selectFn
            }
        })


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

        self.spawnShipAtCity(startingCity, 'Caravel')
        self.spawnShipAtCity(startingCity, 'Caravel')
        self.spawnShipAtCity(startingCity, 'Caravel')

        print "Starting at ", startingCity
        # Close intro modal
        self.removeView()

        self.mapElement.center(startingCity.portX, startingCity.portY)

        self.logMap.setDirectionalInputHandler(self.moveMap)

        # TODO Let the player pick from a few randomly generated captains
        self.player = Captain()
        self.player.gold = 700
        self.mapElement.setPlayer(self.player)

        self.enableGameHandlers()
        self.map.trigger('enterCity', self.player, startingCity)

    def spawnShipAtCity(self, city, type=None):
        types = shipTypes.keys()
        if type is None:
            type = types[randint(len(types) - 1)]
        if type not in types:
            raise KeyError("Can't find ship type[{}]".format(type))
        city.addShip(type)

    def enableGameHandlers(self):
        # Enable our gameplay handlers
        self.enableHandler('windUpdate')
        self.enableHandler('shipsUpdate')

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
