'''
DemoThree GameState
'''
import RoguePy.State.GameState as GameState
from RoguePy.Input import Keys
from RoguePy.UI import Colors
from RoguePy.UI import Elements
from RoguePy.UI import View
from RoguePy.libtcod import Color

class Demo3(GameState):
 
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
    frame.setTitle("Interactive elements")
    self.frame = frame
    self.view.addElement(frame)
    frame.addElement(Elements.Label(3, frame.height - 1, "ESC - Quit"))
    frame.addElement(Elements.Label(35, frame.height - 1, "Spc - Next"))
    
    str = \
      "The Menu element accepts list of dicts. Each key is an item in the menu, and the values " + \
      "are callbacks. The callback will be called when the user selects an option, and will be " + \
      "passed the index of the item that was selected. Press Up/Down/Enter to select a backgroud " + \
      "color for the main frame Element and all of its children.\n\n" + \
      "Sliders allow the user to choose a value within a specified range, and call a callback when " + \
      "their selected value changes.\n\n" + \
      "Press R, G, or B to select the appropriate slider, and the left and right arrows to adjust " + \
      "the values. The sliders' values range from 0 to 255."
    
    halfX = self.view.width / 2
    halfY = self.view.height / 2
    self.frame.addElement(Elements.Text(2, 2, self.view.width - 4, halfY + 1, str))
    
    str2 = \
      "Press TAB to pop up a modal dialog. Modals are accomplished by creating a separate View from " + \
      "from the default view. You can then call the addView method to open the modal. Modals need not " + \
      "be the full size of the screen, and the previous view will be visible behind it. Close a modal View " + \
      "by calling removeView()"
    self.frame.addElement(Elements.Text(14, halfY + 4, 32, 10, str2))

    def makeSetBg(color):
      def setBg(idx):
        self.frame.setDefaultBackground(color, True)
      return setBg
    
    menuItems = [
      {'Black' : makeSetBg(Colors.black)},
      {'Gray'  : makeSetBg(Colors.gray)},
      {'Red'   : makeSetBg(Colors.red)},
      {'Blue'  : makeSetBg(Colors.blue)},
      {'Green' : makeSetBg(Colors.green)}
    ]
    self.menuFrame = self.frame.addElement(Elements.Frame(1, halfY + 4, 12, 6))
    self.menuFrame.setTitle("Bg Color")
    self.menu = self.menuFrame.addElement(Elements.Menu(1, 1, 10, 4, menuItems))
    
    self.sliderFrame = self.frame.addElement(Elements.Frame(1, halfY + 10, 12, 5))
    self.sliderFrame.setTitle("Fg Color")
    
    self.labelR = self.sliderFrame.addElement(Elements.Label(1,1,"R"))
    rVal = self.frame.getDefaultForeGround().r
    self.sliderR = self.sliderFrame.addElement(Elements.Slider(3, 1, 8, 0, 255, rVal, 8))
    self.sliderR.onChange = self.changeForeground
    
    self.labelG = self.sliderFrame.addElement(Elements.Label(1,2,"G"))
    gVal = self.frame.getDefaultForeGround().g
    self.sliderG = self.sliderFrame.addElement(Elements.Slider(3, 2, 8, 0, 255, gVal, 8))
    self.sliderG.onChange = self.changeForeground
    self.sliderG.disable()
    
    self.labelB = self.sliderFrame.addElement(Elements.Label(1,3,"B"))
    bVal = self.frame.getDefaultForeGround().b
    self.sliderB = self.sliderFrame.addElement(Elements.Slider(3, 3, 8, 0, 255, bVal, 8))
    self.sliderB.onChange = self.changeForeground
    self.sliderB.disable()

    #TODO rewrite
    modalText = \
      "The Modal element is simply a wrapper. It has no visual components, but allows you to nest " + \
      "Elements within it. The inputs associated with the modal, and its descendants, will be the " + \
      "only ones processed while the modal is visible. You must bind the Input associated with " + \
      "the modal's hide() method directly to the modal element, rather than, say to the View as " + \
      "even Inputs bound directly to the View are unavailable when a modal is present.\n\n" + \
      "Notice how Space and ESC are no longer available. You may proceed once you've closed this " + \
      "modal and thus re-enabled the View-bound Inputs."
    
    modalX = halfX / 4 - 1
    modalY = halfY / 4
    modalW = halfX * 3 / 2 + 2
    modalH = halfY * 3 / 2
    
    self.modal = View(modalW, modalH, modalX, modalY)
    self.modalFrame = self.modal.addElement(Elements.Frame(0, 0, modalW, modalH))
    self.modalFrame.setTitle("Modal Elements")
    self.modalText = self.modal.addElement(Elements.Text(2, 2, modalW - 4, modalH - 4, modalText))
    self.modalLabel  = self.modal.addElement(Elements.Label(3, modalH - 1, "TAB - Back"))

  def _setupInputs(self):
    self.frame.setKeyInputs({
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
      'showModal': {
        'key': Keys.Tab,
        'ch' : None,
        'fn' : self.toggleModal
      },
      'menuScrollUp': {
        'key' : Keys.Up,
        'ch'  : None,
        'fn'  : self.menu.selectUp
      },
      'menuScrollDn': {
        'key' : Keys.Down,
        'ch'  : None,
        'fn'  : self.menu.selectDown
      },
      'menuSelect': {
        'key' : Keys.Enter,
        'ch'  : None,
        'fn'  : self.menu.selectFn
      }
    })
    
    self.modal.setKeyInputs({
      'showModal': {
        'key': Keys.Tab,
        'ch' : None,
        'fn' : self.toggleModal
      }
    })
    
    self.sliderFrame.setKeyInputs({
      'selectR': {
        'key': None,
        'ch' : "r",
        'fn' : self.selectR
      },
      'selectG': {
        'key': None,
        'ch' : "g",
        'fn' : self.selectG
      },
      'selectB': {
        'key': None,
        'ch' : "b",
        'fn' : self.selectB
      }

    })

    self.modal.setInputs({
      'hideModal': {
        'key': Keys.Tab,
        'ch' : None,
        'fn' : self.closeModal
      }
    })

    def setSliderInputs(slider):
      slider.setKeyInputs({
        'left' : {
          'key' : Keys.Left,
          'ch'  : None,
          'fn'  : slider.left
        },
        'right' : {
          'key' : Keys.Right,
          'ch'  : None,
          'fn'  : slider.right
        }
      })

    setSliderInputs(self.sliderR)
    setSliderInputs(self.sliderG)
    setSliderInputs(self.sliderB)

    self.setFocus(self.sliderR)

  ###
  # Input callbacks
  ###

  def changeForeground(self):
    r = self.sliderR.val
    g = self.sliderG.val
    b = self.sliderB.val
    color = Color(r, g, b)
    self.frame.setDefaultForeground(color, True)
  
  def selectR(self):
    self.sliderR.enable()
    self.sliderG.disable()
    self.sliderB.disable()
    self.setFocus(self.sliderR)
  def selectG(self):
    self.sliderR.disable()
    self.sliderG.enable()
    self.sliderB.disable()
    self.setFocus(self.sliderG)
  def selectB(self):
    self.sliderR.disable()
    self.sliderG.disable()
    self.sliderB.enable()
    self.setFocus(self.sliderB)

  def openModal(self):
    self.addView(self.modal)
  def closeModal(self):
    self.removeView()


  def next(self):
    self.manager.setNextState('demo4')
  def quit(self):
    self.manager.setNextState('quit')
