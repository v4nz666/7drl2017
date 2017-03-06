'''
SplashScreen GameState
'''
import time
from RoguePy.State import GameState
from RoguePy.Input import Keys
from RoguePy.UI import Elements

class SplashScreen(GameState):
  _ticks = 0
  _frame = 0
  _animationComplete = False
  _titleText = "RoguePy"
  _subTitleText = "The easy rogue-like library"
  
  def __init__(self, name, manager):
    super(SplashScreen, self).__init__(name, manager)
    
    self.addHandler('animationHandler', 6, self.renderAnimationFrame)

  def beforeLoad(self):
    self._setupView()
    self._setupInputs()

  def renderAnimationFrame(self):
    self._ticks = self._ticks + 1
    if self._frame >= len(self._subTitleText):
      self.endAnimation()
      return
    
    self._frame = self._frame + 1
    _str = self._subTitleText[:self._frame]
    self.elements['subTitleText'].setText(_str)

  def endAnimation(self):
    self.elements['pressKey'].show()
    self.setFocus(self.elements['pressKey'])
    self._animationComplete = True
    time.sleep(0)
    self.clearViewInputs()
    self.removeHandler('animationHandler')

  def skipAnimation(self):
    self.elements['subTitleText'].setText(self._subTitleText)
    self.endAnimation()

  def clearViewInputs(self):
    self.view.setKeyInputs({})

  def _setupView(self):
    self.elements = {}
    
    titleX = (self.view.width - len(self._titleText)) / 2
    titleY = (self.view.height / 3)
    titleText = Elements.Text(titleX, titleY, len(self._titleText), 1, self._titleText)
    
    subTitleX = (self.view.width - len(self._subTitleText)) / 2
    subTitleY = (self.view.height / 3) + 1
    subTitleText = Elements.Text(subTitleX, subTitleY, len(self._subTitleText), 1)
    
    string = "Press any key (Esc to quit)"
    length = len(string)
    x = (self.view.width - length) / 2
    y = self.view.height - 1
    height = 1
    pressKey = Elements.Text(x, y, length, height, string)
    pressKey.visible = False
    
    self.elements['titleText'] = self.view.addElement(titleText)
    self.elements['subTitleText'] = self.view.addElement(subTitleText)
    self.elements['pressKey'] = self.view.addElement(pressKey)

  def _setupInputs(self):

    self.view.setKeyInputs({
      'skip': {
        'key': 'any',
        'ch': None,
        'fn': self.skipAnimation
      }
    })

    self.elements['pressKey'].setKeyInputs({
      'quit': {
        'key':Keys.Escape,
        'ch': None,
        'fn': self.quit
      },
      'next': {
        'key': 'any',
        'ch': None,
        'fn': self.next
      }
    })


  def next(self):
    self.manager.setNextState('demo1')
  def quit(self):
    self.manager.setNextState('quit')
