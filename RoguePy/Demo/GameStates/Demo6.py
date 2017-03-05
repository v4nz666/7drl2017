"""
Demo6 GameState
"""
import RoguePy.State.GameState as GameState
from RoguePy.Input import Keys
from RoguePy.UI import Elements
from RoguePy.libtcod import libtcod

class Demo6(GameState):
    def __init__(self, name, manager):
        super(self.__class__, self).__init__(name, manager)

    def beforeLoad(self):
        self._setupView()
        self._setupInputs()

    def updateUi(self):
        self.dialVal.clear()
        self.dialVal.setLabel(str(self.dial.getVal()))

    ###
    # Initialisation
    ###

    def _setupView(self):
        frame = Elements.Frame(0, 0, self.view.width, self.view.height)
        frame.setTitle("The Dial Element")
        self.view.addElement(frame)
        frame.addElement(Elements.Label(3, frame.height - 1, "ESC - Quit"))
        frame.addElement(Elements.Label(35, frame.height - 1, "Spc - Next"))

        self.dial = frame.addElement(Elements.Dial(1, 1))
        self.dialVal = frame.addElement(Elements.Label(1, 8, str(self.dial.getVal()), 7))

    def _setupInputs(self):
        self.view.setKeyInputs({
            'quit': {
                'key': Keys.Escape,
                'ch': None,
                'fn': self.quit
            },
            'step': {
                'key': Keys.Space,
                'ch': None,
                'fn': self.next
            }
        })

        def leftClick(mouse):
            charSize = libtcod.sys_get_char_size()

            print "Left!"
            print mouse.x / charSize[0], mouse.y / charSize[1]
        def rightClick(mouse):
            charSize = libtcod.sys_get_char_size()
            print "Left!"
            print mouse.x / charSize[0], mouse.y / charSize[1]

        self.view.setMouseInputs({
            'rClick': rightClick,
            'lClick': leftClick
        })

        self.dial.setKeyInputs({
            'left': {
                'key': Keys.Left,
                'ch': None,
                'fn': self.ccw
            },
            'right': {
                'key': Keys.Right,
                'ch': None,
                'fn': self.cw
            }

        })


    ###
    # Input callbacks
    ###
    def next(self):
        self.manager.setNextState('demo1')

    def quit(self):
        self.manager.setNextState('quit')

    def cw(self):
        self.dial.add(11.25)
        self.updateUi()

    def ccw(self):
        self.dial.sub(11.25)
        self.updateUi()
