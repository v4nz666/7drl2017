import util
from shipTypes import shipTypes, getRandomType
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

from Ship import Ship, ShipPlacementError

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

        self.captains = []

        self.addHandler('fpsUpdate', 60, self.fpsUpdate)
        self.addHandler('windUpdate', config.fps * 2, self.windUpdate)
        self.addHandler('shipsUpdate', 1, self.shipsUpdate, False)
        self.addHandler('infoPanelUpdate', 1, self.infoPanelUpdate, False)

        self.addHandler('daysAtSea', config.fps * 15, self.daysAtSea, False)
        self.addHandler('foodUpdate', config.fps * 15, self.foodUpdate, False)
        self.addHandler('rumUpdate', config.fps * 20, self.rumUpdate, False)

        self.addHandler('aiUpdate', 10, self.aiUpdate, False)

        self.addHandler('generateNews', config.fps * 10, self.generateNews)
        self.addHandler('citiesUpdate', config.fps * 60, self.citiesUpdate)
        self.addHandler('generateCaptains', config.captains['genDelay'], self.generateCaptains, False)

    def enableGameHandlers(self):
        self.enableHandler('generateNews')
        self.enableHandler('generateCaptains')
        self.enableHandler('aiUpdate')
        self.enableHandler('daysAtSea')
        self.enableHandler('foodUpdate')
        self.enableHandler('rumUpdate')
        self.enableHandler('shipsUpdate')
        self.enableHandler('infoPanelUpdate')

    def disableGameHandlers(self):
        self.disableHandler('generateNews')
        self.disableHandler('generateCaptains')
        self.disableHandler('aiUpdate')
        self.disableHandler('daysAtSea')
        self.disableHandler('foodUpdate')
        self.disableHandler('rumUpdate')
        self.disableHandler('shipsUpdate')
        self.disableHandler('infoPanelUpdate')

    def beforeLoad(self):
        self.manager.updateUi(self)
        self.addView(self.introModal)
        self.addHandler('intro', 1, self.doIntro)

    def citiesUpdate(self):
        for c in self.map.cities:
            city = self.map.cities[c]
            if city == self.currentCity:
                continue
            city.gold += randint(city.size * 1000)

        if self.currentCity is not None:
            self.updateCityUI()

    def generateCaptains(self):
        #TODO generate a random number
        count = 1
        cityFails = 0
        while count and len(self.captains) < config.captains['maxCount']:
            if randfloat(1) >= config.captains['genThreshold']:
                print "skipping captain generation"
                continue
            neighbours = []

            while not len(neighbours):
                city = self.map.cities[self.map.cities.keys()[randint(len(self.map.cities) - 1)]]
                neighbours = city.neighbours
            print "Got city {}".format(city.name)
            captain = Captain()
            shipType = getRandomType()
            print "creating ship"
            try:
                ship = Ship(self.map, shipType, city.portX, city.portY)
            except ShipPlacementError:
                print 'failed to place ship, trying a new city'
                cityFails += 1
                if cityFails >= 10:
                    print "Too many city fails!"
                    break
                continue
            cityFails = 0

            captain.setShip(ship)
            captain.lastCity = city

            destination = neighbours[randint(len(neighbours) - 1)]
            if not captain.setDestination(destination):
                print "failed to find a destination"
            else:
                self.captains.append(captain)

                cell = self.map.getCell(ship.mapX, ship.mapY)
                if cell and not cell.entity:
                    self.map.addEntity(ship, ship.mapX, ship.mapY)

                print "Added new captain [{}][{}] at {}-{},{} => {}-{},{}".format(captain.name, shipType, city.name, city.portX, city.portY, destination.name, destination.portX, destination.portY)
            count -= 1

    def generateNews(self):
        cities = self.map.cities
        newsCount = randint(len(cities) / 5)
        print "Generating up to {} news items".format(newsCount)
        while newsCount:
            if randfloat(1) < config.news['genThreshold']:
                name = cities.keys()[randint(len(cities) - 1)]
                cities[name].generateNews()
                print "news at {}".format(name)
            newsCount -= 1

    def daysAtSea(self):
        if not (self.player and self.player.atSea):
            return
        print "Day at sea [-{}]".format(config.morale['daysAtSea'])
        self.player.daysAtSea += 1
        self.player.morale -= config.morale['daysAtSea']
        if self.player.morale <= 0:
            self.player.morale = 0

    def foodUpdate(self):
        if not (self.player and self.player.atSea):
            return

        if self.player.ship.goods['food'] < 1:
            if self.player.daysWithoutFood >= config.morale['daysToStarve']:
                if self.player.ship.crew > 0:
                    self.player.ship.crew -= 1
                print "Starved [{}]".format(config.morale['crewStarved'])
                self.player.morale -= config.morale['crewStarved']
                self.player.daysWithoutFood = 0
            else:
                self.player.daysWithoutFood += 1
                print "Food [{}]".format(config.morale['noFood'])
                self.player.morale -= config.morale['noFood']

            if self.player.morale < 0:
                self.player.morale = 0
        else:
            print "Ate food"
            self.player.ship.takeGoods('food')

    def rumUpdate(self):
        if not (self.player and self.player.atSea):
            return

        if self.player.ship.goods['rum'] < 1:
            print "Rum [{}]".format(config.morale['noRum'])
            self.player.morale -= config.morale['noRum']
            if self.player.morale < 0:
                self.player.morale = 0
        else:
            print "Drank rum"
            self.player.ship.takeGoods('rum')

    def infoPanelUpdate(self):
        self.goldLabel.setLabel(str(self.player.gold).zfill(5))
        self.repLabel.setLabel(self.player.rep)

        self.captainsName.setText(self.player.name).setDefaultForeground(Colors.white)

        for k in self.player.skills.keys():
            getattr(self, "{}Label".format(k)).setLabel(str(self.player.skills[k]).zfill(3))

        if self.player.ship:
            self.myShipTypeLabel.setLabel("{:>11}".format("({})".format(self.player.ship.name)))

            crewStr = "{:>3}".format(self.player.ship.crew)
            crewClr = Colors.dark_green
            if self.player.ship.crew < self.player.ship.stats['minCrew']:
                crewClr = Colors.dark_red

            self.crewCountLabel.setLabel(crewStr).setDefaultForeground(crewClr)
            self.crewMinLabel.setLabel(self.player.ship.stats['minCrew'])
            self.crewMaxLabel.setLabel(self.player.ship.stats['maxCrew'])
            self.moraleLabel.setLabel(self.player.morale, True) \
                .setDefaultForeground(getColor(100 - self.player.morale))

            self.goodsDict.setItems(self.player.ship.goods)

            self.cannonballCountLabel.setLabel(self.player.ship.cannonballs, True)
            self.chainshotCountLabel.setLabel(self.player.ship.chainshot, True)

            hullDmg = self.player.ship.stats['hullDamage']
            self.hullDamageLabel.setDefaultForeground(util.getColor(hullDmg))
            self.hullDamageVal.setLabel("{:>3}".format(hullDmg)).setDefaultForeground(util.getColor(hullDmg))
            sailDmg = self.player.ship.stats['sailDamage']
            self.sailDamageLabel.setDefaultForeground(util.getColor(sailDmg))
            self.sailDamageVal.setLabel("{:>3}".format(sailDmg)).setDefaultForeground(util.getColor(sailDmg))

    def shipsUpdate(self):
        self.playerUpdate()
        self.aiUpdate()

    def playerUpdate(self):
        if self.player.ship:
            self.moveShip(self.player.ship)

    def aiUpdate(self):
        toPurge = []
        for c in self.captains:
            if c.dead:
                print "{} DIED!".format(c.name)
                c.lastCity.addNews("{} was lost at sea.".format(c.name))
                toPurge.append(c)
                continue
            if c.ship.sunk:
                print "{} Sunk!".format(c.name)
                toPurge.append(c)
                continue
            if not c.path:
                print "{} has no path".format(c.name)
                c.ship.anchored = True
            elif not util.pathSize(c.path):
                print "Reached destination!"
                toPurge.append(c)
            elif c.recalculateHeading:
                c.recalculateHeading = False
                c.sinceRecalc = 0
                c.ship.anchored = False
                util.checkPath(self.map, c.ship.mapX, c.ship.mapY, c.destination.portX, c.destination.portY, c.path)

                if not util.pathSize(c.path):
                    print "couldn't repath. Killing"
                    c.dead = True
                x1, y1 = c.ship.mapX, c.ship.mapY
                x2, y2 = util.pathWalk(c.path)
                if x2 is None:
                    # TODO a little harsh, perhaps
                    c.dead = True
                    continue

                heading = int(util.bearing(x1, y1, x2, y2))
                c.ship.heading = heading
                # TODO full speed all the time?
                c.ship.sails = config.maxSails
            if self.moveShip(c.ship):
                if c.sinceRecalc >= config.captains['fovRecalcCooldown']:
                    c.recalculateHeading = True
                c.sinceRecalc += 1




        for c in toPurge:
            print "Purging {}".format(c.name)
            self.captains.remove(c)
            util.deletePath(c.path)
            self.map.removeEntity(c.ship, c.ship.mapX, c.ship.mapY)



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
        # HACK! Keep ships off the dreaded bottom-right corner
        elif ship.mapY >= self.map.height - 1:
            ship.y = self.map.height - 2

        if ship.mapX == oldX and ship.mapY == oldY:
            return False

        destination = self.map.getCell(ship.mapX, ship.mapY)
        if destination and destination.type is not 'water':

            ship.damageHull(config.damage['rocks'])

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
            #TODO Ship detection here...
            #if isinstance(n.entity, Ship):

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
        self.disableGameHandlers()
        self.player.returnToPort()


        if player.ship:
            self.map.removeEntity(player.ship, player.ship.mapX, player.ship.mapY)
        self.currentCity = city
        player.setCity(city)
        self.addView(self.cityModal)
        self.cityMsgs.messages = []
        self.cityMsgs.setDirty(True)
        city.setPrices()
        self.hideShops()
        self.disableShops()
        if not self.player.ship and 'shipyard' in city.shops:
            self.cityShowShop('shipyard')
        else:
            self.cityShowShop('generalStore')

        self.shipyardMenu.selected = 0
        self.shipyardMenu.setDirty(True)
        self.generalstoreMenu.selected = 0
        self.generalstoreMenu.setDirty(True)

        self.updateCityUI()

    def castOff(self, ship):
        if not self.player.ship:
            return False
        if self.player.ship.crew < self.player.ship.stats['minCrew']:
            self.cityMsgs.message("Not enough crew to sail!")
            return False

        self.removeView()
        ship.anchored = True
        ship.heading = 0.0
        ship.sails = 0
        x, y = self.currentCity.portX, self.currentCity.portY
        ship.x = x
        ship.y = y
        self.cityMsgs.message("Casting off from {}".format(self.currentCity.name))
        self.map.addEntity(ship, x, y)
        self.currentCity = None
        self.player.atSea = True

        self.enableGameHandlers()

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
        if not self.player.ship or self.player.ship.crew < self.player.ship.stats['minCrew']:
            self.dockFrame.disable()
        else:
            self.dockFrame.enable()

    def updateShipyardUI(self):
        # Repairs
        rateStr = "${}/{}".format(self.currentCity.repairRate, config.shipyard['repairReturn'])
        self.repairRateVal.setLabel(rateStr)
        if self.player.ship:
            self.yourShipFrame.show()
            hullDamage = self.player.ship.stats['hullDamage']
            sailDamage = self.player.ship.stats['sailDamage']
            hullColor = getColor(hullDamage)
            sailColor = getColor(sailDamage)
            self.repairHullCurrent.setLabel(str(hullDamage)).setDefaultForeground(hullColor)
            self.repairSailCurrent.setLabel(str(sailDamage)).setDefaultForeground(sailColor)

            valueStr = "{:>5}".format(Ship.getSellPrice(self.player.ship.stats))
            self.yourShipValue.setLabel(valueStr).setDefaultForeground(Colors.gold)
            hullDmg = self.player.ship.stats['hullDamage']
            hullStr = "{:>3}".format(hullDmg)
            self.yourShipHullDmg.setLabel(hullStr).setDefaultForeground(util.getColor(hullDmg))
            sailDmg = self.player.ship.stats['sailDamage']
            sailStr = "{:>3}".format(sailDmg)
            self.yourShipSailDmg.setLabel(sailStr).setDefaultForeground(util.getColor(sailDmg))

            if not self.player.ship.goods['wood']:
                self.notEnoughWood.setDefaultForeground(Colors.darker_red)
            else:
                self.notEnoughWood.setDefaultForeground(Colors.darker_green)
            if not self.player.ship.goods['cloth']:
                self.notEnoughCloth.setDefaultForeground(Colors.darker_red)
            else:
                self.notEnoughCloth.setDefaultForeground(Colors.darker_green)
        else:
            self.yourShipFrame.hide()
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

        self.cannonballOnShip.setLabel(balls, True)
        self.chainshotOnShip.setLabel(chain, True)

        # Buy sell ships
        self.shipyardMenu.setItems(self.currentCity.availableShips)
        if not len(self.currentCity.availableShips):
            self.shipyardMenu.disable()
        else:
            self.shipyardMenu.enable()
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
        ][self.generalstoreMenu.selected]

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
            'pause': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.showPause
            },
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
        self.infoPanel = self.view.addElement(Elements.Frame(55, 0, 20, 40, "Info"))
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

        self.infoPanel.addElement(Elements.Label(2, 10, "CAPTAIN")).setDefaultForeground(Colors.flame)
        self.captainsName = self.infoPanel.addElement(Elements.Text(1, 11, self.infoPanel.width - 2, 4, ""))
        self.infoPanel.addElement(Elements.Label(1, 14, "Gold")).setDefaultForeground(Colors.gold)
        self.goldLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 7, 14, "      ")). \
            setDefaultForeground(Colors.gold)
        self.infoPanel.addElement(Elements.Label(1, 15, "Rep")).setDefaultForeground(Colors.lighter_azure)
        self.repLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 15, "000")). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(2, 16, "Skills")).setDefaultForeground(Colors.darker_flame)
        self.infoPanel.addElement(Elements.Label(1, 17, "Nav")).setDefaultForeground(Colors.lighter_azure)
        self.navLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 17, "000")). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 18, "Gun")).setDefaultForeground(Colors.lighter_azure)
        self.gunLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 18, "000")). \
            setDefaultForeground(Colors.azure)



        self.infoPanel.addElement(Elements.Label(2, 19, "SHIP")).setDefaultForeground(Colors.flame)
        self.myShipTypeLabel = self.infoPanel.addElement(Elements.Label(6, 19, "{:>11}".format(""))) \
            .setDefaultForeground(Colors.flame)
        self.infoPanel.addElement(Elements.Label(2, 20, "Crew")).setDefaultForeground(Colors.darker_flame)

        self.infoPanel.addElement(Elements.Label(1, 21, "On Board")).setDefaultForeground(Colors.lighter_azure)
        self.crewCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 21, "{:>3}".format(""))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 22, "Min")).setDefaultForeground(Colors.lighter_azure)
        self.crewMinLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 22, "{:>3}".format(""))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 23, "Max")).setDefaultForeground(Colors.lighter_azure)
        self.crewMaxLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 23, "{:>3}".format(""))). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 24, "Morale")).setDefaultForeground(Colors.lighter_azure)
        self.moraleLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 24, "   ")). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(2, 25, "Damage")).setDefaultForeground(Colors.darker_flame)
        self.hullDamageLabel = self.infoPanel.addElement(Elements.Label(1, 26, "Hull")) \
            .setDefaultForeground(util.getColor(100))
        self.hullDamageVal = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 26, "n/a")) \
            .setDefaultForeground(util.getColor(100))
        self.sailDamageLabel = self.infoPanel.addElement(Elements.Label(1, 27, "Sail")) \
            .setDefaultForeground(util.getColor(100))
        self.sailDamageVal = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 27, "n/a")) \
            .setDefaultForeground(util.getColor(100))


        self.infoPanel.addElement(Elements.Label(2, 28, "AMMO")).setDefaultForeground(Colors.darker_flame)
        self.infoPanel.addElement(Elements.Label(1, 29, "Cannonball")).setDefaultForeground(Colors.lighter_azure)
        self.cannonballCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 29, "   ")). \
            setDefaultForeground(Colors.azure)
        self.infoPanel.addElement(Elements.Label(1, 30, "Chainshot")).setDefaultForeground(Colors.lighter_azure)
        self.chainshotCountLabel = self.infoPanel.addElement(Elements.Label(self.infoPanel.width - 4, 30, "   ")). \
            setDefaultForeground(Colors.azure)

        self.infoPanel.addElement(Elements.Label(2, 31, "CARGO")).setDefaultForeground(Colors.darker_flame)
        self.goodsDict = self.infoPanel.addElement(Elements.Dict(1, 32, self.infoPanel.width - 2, 6)) \
            .setDefaultForeground(Colors.lighter_azure)


        self.helpPanel = self.view.addElement(Elements.Frame(55, 40, 20, 10, "Help"))
        self.helpPanel.addElement(Elements.Label(1, 1, "Lt/Rt")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 1, "Heading L/R")).setDefaultForeground(Colors.azure)
        self.helpPanel.addElement(Elements.Label(1, 2, "Up/Dn")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 2, "Sails Up/Dn")).setDefaultForeground(Colors.azure)
        self.helpPanel.addElement(Elements.Label(1, 4, "TAB")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 4, "Cptn's Log")).setDefaultForeground(Colors.azure)
        self.helpPanel.addElement(Elements.Label(1, 6, "SPC")).setDefaultForeground(Colors.dark_green)
        self.helpPanel.addElement(Elements.Label(7, 6, "Anchor Up/Dn")).setDefaultForeground(Colors.azure)
        self.fpsLabel = self.helpPanel.addElement(Elements.Label(2, self.helpPanel.height - 2, "000fps"))

        halfX = self.view.width / 2
        halfY = self.view.height / 2

        #### Pause menu
        pauseX = self.view.width / 2 - 7
        pauseY = self.view.height / 2 - 2
        pauseW = 13
        pauseH = 4

        self.pauseMenu = View(pauseW, pauseH, pauseX, pauseY)
        self.pauseMenu.addElement(Elements.Frame(0, 0, pauseW, pauseH, "Game Paused")) \
            .setDefaultForeground(Colors.darker_azure)
        self.pauseMenu.addElement(Elements.Label(1, 1, "Esc    Back")) \
            .setDefaultForeground(Colors.azure)
        self.pauseMenu.addElement(Elements.Label(1, 2, " Q     Quit")) \
            .setDefaultForeground(Colors.azure)


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
        modalX = halfX / 4
        modalY = 0
        modalW = halfX * 3 / 2 + 4
        modalH = self.view.height

        self.cityModal = View(modalW, modalH, modalX, modalY)
        self.cityFrame = self.cityModal.addElement(Elements.Frame(0, 0, modalW + 2, modalH + 2, "Welcome!"))
        self.generalStoreFrame = self.cityModal.addElement(Elements.Frame(1, 1, 28, 16, 'GE(N)ERAL STORE'))
        self.tavernFrame = self.cityModal.addElement(Elements.Frame(1, 17, 28, 11, '(T)AVERN'))
        self.dockFrame = self.cityModal.addElement(Elements.Frame(1, 28, 14, 10, 'DOC(K)'))
        self.gossipFrame = self.cityModal.addElement(Elements.Frame(15, 28, 14, 10, '(G)OSSIP'))
        self.shipyardFrame = self.cityModal.addElement(Elements.Frame(29, 1, 29, 27, 'SHIP (Y)ARD'))
        self.brothelFrame = self.cityModal.addElement(Elements.Frame(29, 28, 29, 10, '(B)ROTHEL'))
        self.cityMsgFrame = self.cityModal.addElement(Elements.Frame(1, modalH - 12, modalW - 2, 11, "Messages"))
        self.cityMsgFrame._chars = {k: ' ' for k in ['tl', 't', 'tr', 'r', 'br', 'b', 'bl', 'l']}
        self.cityMsgs = self.cityMsgFrame.addElement(
            Elements.MessageScroller(1, 1, self.cityMsgFrame.width - 2, self.cityMsgFrame.height - 2))

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

        self.generalstoreMenu = self.generalStoreFrame.addElement(
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
        self.shipSpecFrame = self.shipSaleFrame.addElement(Elements.Frame(13, 1, 13, 11, "Ship Specs"))
        self.shipSpecs = self.shipSpecFrame.addElement(Elements.Dict(1, 1, 11, 8))
        self.damageLabel = self.shipSpecFrame.addElement(Elements.Label(4, 7, "Damage"))
        self.damageSpecs = self.shipSpecFrame.addElement(Elements.Dict(1, 8, 11, 2)).setItems({
            'hull': 85,
            'sail': 12
        })
        self.yourShipFrame = self.shipSaleFrame.addElement(Elements.Frame(13, 12, 13, 4, "Your Ship"))
        for k in ['r', 'br', 'b', 'bl', 'l']:
            self.yourShipFrame._chars[k] = " "
        self.yourShipFrame._chars['tl'] = libtcod.CHAR_HLINE
        self.yourShipFrame._chars['tr'] = libtcod.CHAR_HLINE

        self.yourShipFrame.addElement(Elements.Label(0, 1, "Value"))
        self.yourShipFrame.addElement(Elements.Label(0, 2, "Hull Dmg"))
        self.yourShipFrame.addElement(Elements.Label(0, 3, "Sail Dmg"))
        self.yourShipValue = self.yourShipFrame.addElement(Elements.Label(self.yourShipFrame.width - 5, 1, "00000"))
        self.yourShipHullDmg = self.yourShipFrame.addElement(Elements.Label(self.yourShipFrame.width - 3, 2, "000"))
        self.yourShipSailDmg = self.yourShipFrame.addElement(Elements.Label(self.yourShipFrame.width - 3, 3, "000"))

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
        self.hireRateLabel = self.tavernFrame.addElement(Elements.Label(2, 9, "Hire rate-  "))

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
        self.cityMsgs.setDefaultForeground(Colors.white)

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

        self.yourShipFrame.setDefaultColors(Colors.lighter_sepia, Colors.darkest_sepia, True)


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

    def showPause(self):
        self.addView(self.pauseMenu)
        self.paused = True
    def cancelPause(self):
        self.paused = False
        self.removeView()

    def setupInputs(self):
        def killKrew(self):
            self.player.ship.crew -= 1
            if self.player.ship.crew < 0:
                self.player.ship.crew = 0
        # Inputs. =================================================================================
        self.pauseMenu.setKeyInputs({
            # TODO remove
            'quit': {
                'key': None,
                'ch': 'q',
                'fn': self.quit
            },
            'back': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.cancelPause
            },
        })
        self.view.setKeyInputs({
            #TODO remove
            'KILL': {
                'key': None,
                'ch': 'K',
                'fn': lambda: killKrew(self)
            },
            'pause': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.showPause
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

        self.view.setMouseInputs({
            'lClick': self.fireCannon,
            'rClick': self.fireChain
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
            'postScore': {
                'key': None,
                'ch': '[',
                'fn': self.postScore
            },
            'getScore': {
                'key': None,
                'ch': ']',
                'fn': self.getScore
            },

            'pause': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.showPause
            },
            'castOff': {
                'key': None,
                'ch': 'k',
                'fn': lambda:
                self.castOff(self.player.ship)
            },
            'castOff2': {
                'key': None,
                'ch': 'K',
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

        self.generalstoreMenu.setKeyInputs({
            'storeMenuUp': {
                'key': Keys.Up,
                'ch': 'w',
                'fn': lambda: self.generalstoreMenu.selectUp() and
                              self.updateBuySellPrices()
            },
            'storeMenuUp2': {
                'key': Keys.NumPad8,
                'ch': 'W',
                'fn': lambda: self.generalstoreMenu.selectUp() and
                              self.updateBuySellPrices()
            },
            'storeMenuDn': {
                'key': Keys.Down,
                'ch': 's',
                'fn': lambda: self.generalstoreMenu.selectDown() and
                              self.updateBuySellPrices()
            },
            'storeMenuDn2': {
                'key': Keys.NumPad2,
                'ch': 'S',
                'fn': lambda: self.generalstoreMenu.selectDown() and
                              self.updateBuySellPrices()
            },
            'buy': {
                'key': Keys.Left,
                'ch': 'a',
                'fn': lambda:
                self.buyGoods(self.generalstoreMenu.selected)
            },
            'buy2': {
                'key': Keys.NumPad4,
                'ch': 'A',
                'fn': lambda:
                self.buyGoods(self.generalstoreMenu.selected)
            },
            'sell': {
                'key': Keys.Right,
                'ch': 'd',
                'fn': lambda:
                self.sellStuff(self.generalstoreMenu.selected)
            },
            'sell2': {
                'key': Keys.NumPad6,
                'ch': 'D',
                'fn': lambda:
                self.sellStuff(self.generalstoreMenu.selected)
            },
        })
        self.shipyardMenu.setKeyInputs({
            'shipMenuUp': {
                'key': Keys.Up,
                'ch': None,
                'fn': lambda: self.shipyardMenu.selectUp() and
                              self.updateShipStats()
            },
            'shipMenuUp2': {
                'key': Keys.NumPad8,
                'ch': None,
                'fn': lambda: self.shipyardMenu.selectUp() and
                              self.updateShipStats()
            },
            'shipMenuDn': {
                'key': Keys.Down,
                'ch': None,
                'fn': lambda: self.shipyardMenu.selectDown() and
                              self.updateShipStats()
            },
            'shipMenuDn2': {
                'key': Keys.NumPad2,
                'ch': None,
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
                'ch': 'r',
                'fn': self.buyRound

            },
            'buyRound2': {
                'key': None,
                'ch': 'R',
                'fn': self.buyRound
            }
        })

        self.gossipFrame.setKeyInputs({
            'gossip': {
                'key': None,
                'ch': 'g',
                'fn': self.gossip
            },
            'gossip2': {
                'key': None,
                'ch': 'G',
                'fn': self.gossip
            }
        })

    def fire(self, mouse, left=True):
        if not (self.player and self.player.ship):
            return
        charSize = libtcod.sys_get_char_size()
        x, y = self.mapElement.fromScreen(mouse.x / charSize[0], mouse.y / charSize[1])

        if x == -1 or y == -1:
            return

        if self.player.ship.canFire(x, y):
            if left:
                self.player.ship.fireCannon(x, y)
            else:
                self.player.ship.fireChain(x, y)

        #TODO remove
        c = self.map.getCell(x, y)
        if c.entity:
            print c.entity

    def fireChain(self, mouse):
        self.fire(mouse, left=False)

    def fireCannon(self, mouse):
        self.fire(mouse, left=True)

    def gossip(self):
        if not len(self.currentCity.news):
            news = "Seems pretty quiet 'round here"
        else:
            index = randint(len(self.currentCity.news) - 1)
            news = self.currentCity.news[index]
            self.currentCity.removeNews(index)
        self.cityMsgs.message(news)


    def hireCrew(self):
        if not self.player.ship:
            self.cityMsgs.message("Why would you need a crew? You don't even have a ship.")
            return False
        if self.player.ship.crew >= self.player.ship.stats['maxCrew']:
            self.cityMsgs.message("Crew roster is full already")
            return False

        rate = self.currentCity.hireRate
        if self.player.gold >= rate and self.currentCity.hireCrewMember():
            self.player.ship.crew += 1
            self.player.gold -= rate
            self.updateCityUI()
            self.cityMsgs.message("Hired crew member for ${}".format(rate))
            return True
        else:
            self.cityMsgs.message("Can't afford to hire crew")
            return False

    def buyRound(self):

        if not self.player.ship:
            crew = 0
        else:
            crew = self.player.ship.crew
        rate = (crew + 1)
        if self.player.gold >= rate:
            increase = config.tavern['drinkMorale']
            if not self.player.moraleAdjust(increase):
                self.cityMsgs.message("The crew couldn't be much happier. They'll gladly keep drinking, though!")
            else:
                self.cityMsgs.message("Bought a round for ${}, the men seem more happy, now.".format(rate, increase))
            self.player.gold -= rate
            self.updateCityUI()

            return True
        else:
            return False

    def buyCannon(self):
        if not self.player.ship:
            self.cityMsgs.message("No ship to store ammo.")
            return False

        count = config.shipyard['ammoBuyCount']
        if not self.player.ship.addCannonballs(count):
            self.cityMsgs.message("No room for ammo.")
            return False
        self.cityMsgs.message("Bought {} cannonballs for ${}.".format(count, self.currentCity.ammoRate))
        self.player.gold -= self.currentCity.ammoRate
        self.updateCityUI()

    def buyChain(self):
        if not self.player.ship:
            self.cityMsgs.message("No ship to store ammo.")
            return False

        count = config.shipyard['ammoBuyCount']
        if not self.player.ship.addChainshot(count):
            self.cityMsgs.message("No room for ammo.")
            return False
        self.cityMsgs.message("Bought {} chainshot for ${}.".format(count, self.currentCity.ammoRate))
        self.player.gold -= self.currentCity.ammoRate
        self.updateCityUI()

    def repairHull(self):
        if not self.player.ship:
            self.cityMsgs.message("No ship to repair hull.")
            return False
        cost = self.currentCity.repairRate
        if self.player.gold < cost:
            self.cityMsgs.message("Not enough gold to repair hull.")
            return False

        if not self.player.ship.takeGoods('wood'):
            self.cityMsgs.message("Hull repair requires wood.")
            return False

        if self.player.ship.repairHull():
            self.cityMsgs.message("Hull repaired.")
            self.player.gold -= cost
            self.updateCityUI()

    def repairSails(self):
        if not self.player.ship:
            self.cityMsgs.message("No ship to repair sails.")
            return False
        cost = self.currentCity.repairRate
        if self.player.gold < cost:
            self.cityMsgs.message("Not enough gold to repair sails.")
            return False

        if not self.player.ship.takeGoods('cloth'):
            self.cityMsgs.message("Sail repair requires cloth.")
            return False

        if self.player.ship.repairSails():
            self.cityMsgs.message("Sails repaired.")
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
            self.cityMsgs.message("Bought a new {}!".format(shipType))
            self.shipyardMenu.selected = 0
            self.updateCityUI()
        else:
            self.cityMsgs.message("Can't afford to buy {}".format(shipType))

    def brothel(self):
        if self.player.ship:
            crew = self.player.ship.crew
        else:
            crew = 0
        cost = self.currentCity.brothelRate * (crew + 1)
        if self.player.gold >= cost:
            self.cityMsgs.message(
                "The crew will surely remember that night for some time! Everyone is in great spirits.")
            self.player.moraleAdjust(self.currentCity.brothelReturn)
            self.player.gold -= cost
            self.updateCityUI()
        else:
            self.cityMsgs.message("You can't afford a trip to the brothel.")

    def buyGoods(self, index):
        if not self.player.ship:
            self.cityMsgs.message("You don't have a ship to store any goods in.")
            return

        itemName = self.getItemByIndex(index)
        price = self.currentCity.getBuyPrice(itemName)

        if self.player.gold < price:
            self.cityMsgs.message("Not enough gold for {}.".format(itemName))
            return
        if self.currentCity.goods[itemName] < 1:
            self.cityMsgs.message("{} is out of stock.".format(itemName))
            return
        if not self.player.ship.addGoods(itemName):
            self.cityMsgs.message("{} won't fit on ship!".format(itemName))
            return

        self.currentCity.goods[itemName] -= 1
        self.currentCity.gold += price
        self.player.gold -= price


        self.cityMsgs.message("Bought {} for ${}".format(itemName, price))
        self.updateCityUI()

    def sellStuff(self, index):
        if not self.player.ship:
            self.cityMsgs.message("You don't have anything to sell")
            return

        itemName = self.getItemByIndex(index)
        price = self.currentCity.getSellPrice(itemName)

        if self.currentCity.gold < price:
            self.cityMsgs.message("City doesn't have enough gold")
            return
        if not self.player.ship.takeGoods(itemName):
            self.cityMsgs.message("What kinda scam are you trying to pull?")
            return
        self.currentCity.goods[itemName] += 1
        self.player.gold += price
        self.currentCity.gold -= price
        self.updateCityUI()

    @staticmethod
    def getItemByIndex(index):
        return['food', 'rum', 'wood', 'cloth', 'coffee', 'spice'][index]

    def cityShowShop(self, name):
        element = getattr(self, '{}Frame'.format(name))
        if element.visible:
            self.disableShops()
            element.enable()

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
        self.hireRateLabel.setLabel('HireRate-{}'.format(self.currentCity.hireRate))
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

        types = ['Caravel', 'Sloop']
        for i in range(randint(3, 1)):
            shipType = types[randint(1)]

            self.spawnShipAtCity(startingCity, shipType)

        # Close intro modal
        self.removeView()

        self.mapElement.center(startingCity.portX, startingCity.portY)

        self.logMap.setDirectionalInputHandler(self.moveMap)

        # TODO Let the player pick from a few randomly generated captains
        self.player = Captain()
        self.player.gold = 700
        self.mapElement.setPlayer(self.player)

        self.map.trigger('enterCity', self.player, startingCity)

    def spawnShipAtCity(self, city, type=None):
        types = shipTypes.keys()
        if type is None:
            type = types[randint(len(types) - 1)]
        if type not in types:
            raise KeyError("Can't find ship type[{}]".format(type))
        city.addShip(type)

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



    def postScore(self):
        self.cityMsgs.message("POSTing score...")

    def getScore(self):
        self.cityMsgs.message("GETing scores...")