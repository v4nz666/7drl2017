
from .. import UI
from .. import State

class Game:
    def __init__(self, title, width, height, fullscreen):
        print title, width, height, fullscreen
        self.ui = UI.UI()
        self.ui.init(width, height, fullscreen, title)
        self.stateManager = State.StateManager(self.ui)

    def addState(self, state):
        state.manager = self.stateManager
        # Order is important here, as addState() provides the View which is used by init()...
        self.stateManager.addState(state)
        state.init()

    def run(self, stateName):
        self.stateManager.setCurrentState(stateName)
        while not self.ui.is_closed():
            self.stateManager.doTick()
