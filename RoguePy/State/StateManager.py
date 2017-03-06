"""
StateManager
"""


class StateManager():
  def __init__(self, ui):
    self._states = {}
    self._currentState = None
    self._nextState = None

    self.ui = ui

    self.tick = 0
  
  def addState(self, gameState):
    self._states[gameState.name] = gameState
    gameState.initView(self.ui)
    return gameState
  def getState(self, stateName):
    if stateName in self._states:
      return self._states[stateName]
    else:
      return None

  @property
  def ui(self):
    return self.__ui
  @ui.setter
  def ui(self, ui):
    self.__ui = ui

  def getCurrentState(self):
    return self._currentState
  def setCurrentState(self, stateName):
    self.tick = 0
    newState = self._states[stateName]
    newState.beforeLoad()
    self._currentState = newState
    
  def getNextState(self):
    return self._nextState
  def setNextState(self, stateName):
    self._nextState = self._states[stateName]

  def doTick(self):
    state = self._currentState

    handlers = state.tickHandlers
    for h in handlers:
      handler = state.tickHandlers[h]
      if not self.tick % handler.interval:
        handler.run()
    state.purgeHandlers()

    self.tick += 1

    if self.ui:
      self.ui.refresh(state.view)

    state.processInput()

    self.stateTransition()

  def stateTransition(self):
    if self._nextState and self._currentState != self._nextState:
      self._currentState.beforeUnload()
      self._currentState = self._nextState
      self._currentState.beforeLoad()
      self._nextState = None
      self.tick = 0
