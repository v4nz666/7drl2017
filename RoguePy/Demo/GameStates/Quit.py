'''
Quit GameState
'''
import sys
import RoguePy.State.GameState as GameState

class Quit(GameState):
  def __init__(self, name, manager):
    super(Quit, self).__init__(name, manager)
    self.addHandler('quit', 1, self.quit)

  def quit(self):
    print "Quiting!"
    sys.exit()