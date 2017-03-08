'''
GameState
'''
from RoguePy import Input
from RoguePy.UI import View
from TickHandler import TickHandler


class GameState(object):
  def __init__(self, name, manager=None):
    self.name = name
    self.manager = manager
    self.inputHandler = Input.InputHandler()

    self.tickHandlers = {}
    self.handlerQueue = []
    
    self.focused = None

  # Clear all existing views, and create one covering the entire ui
  def initView(self, ui):
    self.__views = [View(ui.width, ui.height)]

  # Add a view onto the stack
  def addView(self, view):
    self.__views.append(view)
  # Pop a view off the stack
  def removeView(self, hack=None):
    if not len(self.__views) > 1 :
      raise IndexError("Tried to close last View on stack")
    return self.__views.pop()


  @property
  def name(self):
    return self.__name
  @name.setter
  def name(self,name):
    self.__name = name
  
  @property
  def manager(self):
    return self.__manager
  @manager.setter
  def manager(self,manager):
    self.__manager = manager
  
  @property
  def inputHandler(self):
    return self.__inputHandler
  @inputHandler.setter
  def inputHandler(self, h):
    if isinstance(h, Input.InputHandler):
      self.__inputHandler = h

  @property
  def view(self):
    return self.__views[-1]

  def addHandler(self, name, interval, handler):
    if not name in self.tickHandlers:
      self.tickHandlers[name] = TickHandler(interval, handler)
  def removeHandler(self, name):
    self.handlerQueue.append(name)

  def disableHandler(self, name):
    print 'disabling[{}]'.format(name)
    if name in self.tickHandlers:
      self.tickHandlers[name].enabled = False
  def enableHandler(self, name):
    print 'enabling[{}]'.format(name)

    if name in self.tickHandlers:
      self.tickHandlers[name].enabled = True

  def purgeHandlers(self):
    for name in self.handlerQueue:
      if name in self.tickHandlers:
        del self.tickHandlers[name]
    self.handlerQueue = []

  def processInput(self):
    key, mouse = self.view.getActiveInputs()
    self.inputHandler.setKeyInputs(key)
    self.inputHandler.setMouseInputs(mouse)
    self.inputHandler.handleInput()

  def setFocus(self, el):
    self.focused = el

  def blur(self):
    self.focused = None

  def beforeLoad(self):
    pass
  def beforeUnload(self):
    pass
