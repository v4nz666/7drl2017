"""
DemoFive GameState
"""
import RoguePy
from RoguePy.Map.Map import Map
from RoguePy.Map.Terrain import Terrain
from RoguePy.Map.Entity import Entity
from RoguePy.Map import terrains

import RoguePy.State.GameState as GameState
from RoguePy.Input import Keys
from RoguePy.UI import Colors
from RoguePy.UI import Elements

class Demo5(GameState):

  def __init__(self,name, manager):

    super(self.__class__, self).__init__(name, manager)

    self.addHandler('updateUi', 1, self.updateUi)

    grid = [
      "               XXXXXXXXX ",
      "  XXXXXX   XXXXX-------X ",
      "  X----XXXXX---X-------X ",
      "  X------------X-------X ",
      "  X----XXXXX---X-------X ",
      "  XX-XXX   X---XXXXXX-XX ",
      "   X-X     X---X    X-X  ",
      "   X-X     XXX-X  XXX-X  ",
      " XXX-XXXXXXX X-XXXX---X  ",
      " X---------X X--------X  ",
      " X--~~~~---X XXXXXX---X  ",
      " X---------X      XXXXX  ",
      " XXXXXXXXXXX             ",
      ]

    water = Terrain(True, False, 'Pool of water') \
      .setChar('~') \
      .setColors(Colors.blue, Colors.darker_blue)

    # This initialises a new empty map
    self.map = Map(len(grid[0]), len(grid))

    statue = Entity('Golden Statue')
    statue.setChar('&')
    statue.setColor(Colors.gold)

    self.map.getCell(20, 9).entity = statue

    for y in range(len(grid)):
      row = grid[y]
      for x in range(len(row)):
        char = row[x]

        if char == "X":
          self.map.getCell(x, y).setTerrain(terrains.WALL)
        elif char == "-":
          self.map.getCell(x, y).setTerrain(terrains.FLOOR)
        elif char == "~":
          self.map.getCell(x, y).setTerrain(water)
        else:
          self.map.getCell(x, y).setTerrain(terrains.EMPTY)


  def beforeLoad(self):
    self._setupView()
    self._setupInputs()
    self.selectedX = 0
    self.selectedY = 0

  def _setupView(self):

    frame = Elements.Frame(0, 0, self.view.width, self.view.height)
    frame.setTitle("The Map")
    self.view.addElement(frame)
    frame.addElement(Elements.Label(3, frame.height - 1, "ESC - Quit"))
    frame.addElement(Elements.Label(35, frame.height - 1, "Spc - Next"))
    self.frame = frame

    str = \
      "The Map Element, along with the RoguePy.Map package allow you to easily define and display " + \
      "the game world. The Map Element allows you to draw a portion of the map, centered around a " + \
      "given coordinate, and allows you to easily navigate between on-map and on-screen coordinates.\n\n" + \
      "Maps are fundamentally made up of terrain. There are a few pre-made terrain definitions EMPTY, " + \
      "WALL, and FLOOR for instance) but you may add as many as you like. Each terrain type has " + \
      "a character, fg and bg color, and may be transparent and/or passable.\n\n"
    str2 = \
      "Move the + around with the arrow keys, and examine the different terrain types.\n\n" + \
      "The crosshair effect is achieved by adding a raw Element to the Map element, setting the " + \
      "background opacity to 0, then simply drawing the + at the onscreen coordinates each frame."

    self.view.addElement(Elements.Text(1, 2, 30, 20, str))
    self.view.addElement(Elements.Text(1, 23, 46, 8, str2))


    self.mapFrame = self.frame.addElement(Elements.Frame(32, 2, 15, 15)).setTitle('Map')
    self.mapElement = self.mapFrame.addElement(Elements.Map(1, 1, 13, 13, self.map))
    self.mapOverlay = self.mapElement.addElement(Elements.Element(0, 0, 13, 13))
    self.mapOverlay.bgOpacity = 0
    self.mapOverlay.draw = self.drawOverlay

    self.fpsLabel = self.mapFrame.addElement(Elements.Label(8, 0, ""))

    self.cellLabel = self.frame.addElement(Elements.Label(32, 18, ""))
    self.cellDesc = self.frame.addElement(Elements.Text(32, 20, 14, 1)).setDefaultColors(Colors.darker_green)
    self.cellItems = self.frame.addElement(Elements.List(32, 21, 14, 1)).setDefaultColors(Colors.gold)

  def _setupInputs(self):
    self.view.setKeyInputs({
      'quit': {
        'key': Keys.Escape,
        'ch' : None,
        'fn' : self.quit
      },
      'step': {
        'key': Keys.Space,
        'ch' : None,
        'fn' : self.next
      },
    })
    self.mapElement.setKeyInputs({
      'selectionUp': {
        'key': Keys.Up,
        'ch' : None,
        'fn' : self.moveSelectionUp
      },
      'selectionDn': {
        'key': Keys.Down,
        'ch' : None,
        'fn' : self.moveSelectionDown
      },
      'selectionLeft': {
        'key': Keys.Left,
        'ch' : None,
        'fn' : self.moveSelectionLeft
      },
      'selectionRight': {
        'key': Keys.Right,
        'ch' : None,
        'fn' : self.moveSelectionRight
      }
    })

  ###
  # Game Loop stuff
  ###

  def updateUi(self):
    m = self.mapElement
    m.center(self.selectedX, self.selectedY)
    self.updateCellDesc()
    self.updateCellItems()
    self.fpsLabel.setLabel("FPS:" + str(RoguePy.getFps()))

  def drawOverlay(self):
    onScreen = self.mapElement.onScreen(self.selectedX, self.selectedY)
    self.mapOverlay.clear()
    self.mapOverlay.putCh(onScreen[0], onScreen[1], '+', Colors.light_green, Colors.black)

  def updateCellDesc(self):
    self.cellLabel.setLabel('Cell:' + str((self.selectedX, self.selectedY)))
    cellTerrain = self.map.getTerrain(self.selectedX, self.selectedY)
    self.cellDesc.setText(cellTerrain.desc)
  def updateCellItems(self):
    e = self.map.getCell(self.selectedX, self.selectedY).entity
    itemNames = []

    if e != None:
      itemNames.append(e.name)
    self.cellItems.setItems(itemNames)


  ###
  # Input callbacks
  ###

  def moveSelectionUp(self):
    if self.selectedY > 0:
      self.selectedY -= 1

  def moveSelectionDown(self):
    if self.selectedY < self.map.height - 1:
      self.selectedY += 1

  def moveSelectionLeft(self):
    if self.selectedX > 0:
      self.selectedX -= 1

  def moveSelectionRight(self):
    if self.selectedX < self.map.width - 1:
      self.selectedX += 1

  def next(self):
    self.manager.setNextState('demo6')
  def quit(self):
    self.manager.setNextState('quit')
