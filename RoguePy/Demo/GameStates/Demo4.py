"""
DemoFour GameState
"""
import RoguePy.State.GameState as GameState
from RoguePy.Input import Keys
from RoguePy.UI import Colors
from RoguePy.UI import Elements

class Demo4(GameState):
  
  def __init__(self,name, manager):
    super(self.__class__, self).__init__(name, manager)
    self._initPlayer()

  def beforeLoad(self):
    self._setupView()
    self._setupInputs()

  def beforeUnload(self):
    self._initPlayer()
    self.playerStatFrame.enable()
    self.updateStats()

  ###
  # Initialisation
  ###

  def _initPlayer(self):
    self.player = Fighter()

  def _setupView(self):
    
    frame = Elements.Frame(0, 0, self.view.width, self.view.height)
    frame.setTitle("The list goes on")
    frame.addElement(Elements.Label(3, frame.height - 1, "ESC - Quit"))
    frame.addElement(Elements.Label(35, frame.height - 1, "Spc - Next"))
    
    str1 = \
      "The player's health is a Bar element, which accepts a min, max and value. It can be given " + \
      "a color for both min and max, and will blend between them. You may also override the chars " + \
      "that are used to represent full and partial blocks.\n\n" + \
      "The Dict Element accepts a dict, and prints the keys and values as if the keys were labels. " + \
      "A Dict has been used for the rest of the stats. Dicts act much like lists, and can be made " + \
      "scrollable if they have more content than can be displayed within their height, and have had " + \
      "inputs attached to their scrollUp and scrollDown methods."
    frame.addElement(Elements.Text(2, 2, 26, self.view.height - 4, str1))
    self.frame = self.view.addElement(frame)
    
    str2 = \
      "Press the A key to do some damage to the Player. Once he dies, the stats frame will be Disabled."
    frame.addElement(Elements.Text(30, 16, 16, 15, str2))
    self.frame = self.view.addElement(frame)

    self.playerStatFrame = frame.addElement(Elements.Frame(30, 4, 14, 8))
    self.playerStatFrame.setTitle('Player stats')
    
    self.playerStatFrame.addElement(Elements.Label(1, 1, "hp"))
    self.playerHpBar = self.playerStatFrame.addElement(Elements.Bar(8, 1, 5))\
      .setMax(self.player.maxHp)\
      .setVal(self.player.hp)\
      .setMinColor(Colors.dark_red)\
      .setMaxColor(Colors.dark_green)
    self.playerStatsDict = self.playerStatFrame.addElement(Elements.Dict(1, 2, 12, 5))\
      .setItems(self.player.stats)
    
  def _setupInputs(self):
    self.view.setKeyInputs({
      'quit': {
        'key': Keys.Escape,
        'ch': None,
        'fn': self.quit
      },
      'step': {
        'key':Keys.Space,
        'ch': None,
        'fn': self.next
      }
    })
    
    self.playerStatFrame.setKeyInputs({
      'attack': {
        'key':None,
        'ch': 'A',
        'fn': self.attack
      }
    })

  def tick(self):
    self.updateStats()
  
  def updateStats(self):
    self.playerHpBar.setVal(self.player.hp)
  
  ###
  # Input callbacks
  ###

  def attack(self):
    if not self.playerStatFrame.enabled:
      return

    self.player.hp -= 1
    if self.player.hp <= 0:
      self.playerStatFrame.disable()
    self.updateStats()

  def next(self):
    self.manager.setNextState('demo5')
  def quit(self):
    self.manager.setNextState('quit')


class Fighter:
  def __init__(self):
    self.hp = 15
    self.maxHp = 15
    self.stats = {
      'strength': 7,
      'defense':  7,
      'dodge':    6,
      'stamina':  5,
      'luck':     9
    }
