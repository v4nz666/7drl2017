"""
DemoTwo GameState
"""
import RoguePy.State.GameState as GameState
from RoguePy.Input import Keys
from RoguePy.UI import Elements

class Demo2(GameState):
 
  def __init__(self,name, manager):
    super(self.__class__, self).__init__(name, manager)
  def beforeLoad(self):
    self._setupView()
    self._setupInputs()
 
  ###
  # Initialisation
  ###
 
  def _setupView(self):
    
    frame = Elements.Frame(0, 0, self.view.width, self.view.height)
    frame.setTitle("Basic Elements")
    self.view.addElement(frame)
    frame.addElement(Elements.Label(3, frame.height - 1, "ESC - Quit"))
    frame.addElement(Elements.Label(35, frame.height - 1, "Spc - Next"))
    
    str = \
      "This is a Text element, it word-wraps a string into a given rectangle.\n\n" + \
      "The border around the view is a Frame element, with an optional title.\n\n" + \
      "The list element accepts an array of strings, and prints them. Hooking user input, Lists " + \
      "can be scrollable. Press the up and down arrows to scroll the inventory.\n\n" + \
      "The inventory list is nested in the frame around it. Nested elements will not be " + \
      "displayed when their parent element isn't visible. Press TAB to show/hide the inventory's Frame."
    str2 =\
      "Inputs may be bound to the view, in which case they are always active (except when a modal " + \
      "element is shown), or bound to elements. Inputs bound to an element are only active when the " + \
      "element, and its parents are active."
    
    self.view.addElement(Elements.Text(1, 2, 22, self.view.height - 4, str))
    self.view.addElement(Elements.Text(27, 15, 18, self.view.height / 2, str2))
    
    inv = [
      "Mandrake Root",
      "Brass Key",
      "Broadsword",
      "Dagger",
      "Leather Armor",
      "Shield",
      "Piece of paper",
      "Glowing Gem",
      "Lockpick",
      "Thieves toolkit",
      "Guild Licence",
      "Green Fur",
      "Fairy Dust",
      "Flask of Water",
      "Cheetaur Claw",
      "Troll beard",
      "Dispel Potion",
      "Undead Unguent"
    ]
    
    invFrame = Elements.Frame(27, 3, 18, 11)
    invFrame.setTitle("Inventory")
    self.list = invFrame.addElement(Elements.List(1, 1, 16, 9, inv))
    
    self.invFrame = self.view.addElement(invFrame)
  
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
      'toggleInv': {
        'key': Keys.Tab,
        'ch' : None,
        'fn' : self.toggleInv
      }
    })
    
    self.list.setKeyInputs({
      'scrollUp': {
        'key': Keys.Up,
        'ch' : None,
        'fn' : self.list.scrollUp
      },
      'scrollDn': {
        'key': Keys.Down,
        'ch' : None,
        'fn' : self.list.scrollDown
      },
    })

  ###
  # Input callbacks
  ###
  
  def toggleInv(self):
    self.invFrame.toggleVisible()
    
  def next(self):
    self.manager.setNextState('demo3')
  def quit(self):
    self.manager.setNextState('quit')
