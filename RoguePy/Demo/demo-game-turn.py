"""
Demo of a minimalist, turn-based rogue-like using the new Game functionality.
TODO: Make this more organized and minimalist.
"""

# Shenanigans to get RoguePy in the search path when it's the project root.
import os, sys
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.append(path)

import RoguePy
from RoguePy.Input import Keys
from RoguePy.UI import Elements

class MainState(RoguePy.GameState):
    def init(self):
        # "World". ================================================================================
        self.map = RoguePy.Game.Map.FromStringList([
            "#########ww#########",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "w..................w",
            "w..................w",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#..................#",
            "#########dd#########",
        ])

        # Note that Entity instances automatically add themselves to the given map on construction.
        player = RoguePy.Game.Entity(self.map,  1,  1, 'Mikey', '@', RoguePy.UI.Colors.white)
        others = [
            RoguePy.Game.Entity(self.map, 10, 10, 'dog',     'd', RoguePy.UI.Colors.white),
            RoguePy.Game.Entity(self.map, 11, 10, 'cat',     'f', RoguePy.UI.Colors.copper),
            RoguePy.Game.Entity(self.map,  9, 11, 'cat-dog', 'e', RoguePy.UI.Colors.dark_crimson),
        ]

        # View. ===================================================================================
        w = 20
        h = 10
        frameStats = Elements.Frame(0, 0, w, h, "Stats")
        frameMessages = Elements.Frame(0, h, w, self.view.height - h, "Messages")
        messages = Elements.MessageScroller(1, 1, frameMessages.width - 2, frameMessages.height - 2)
        messages.setDefaultColors(RoguePy.UI.Colors.lightest_green, RoguePy.UI.Colors.darkest_purple)
        # Not to be confused with Game.Map...
        map = Elements.Map(w, 0, self.view.width - w, self.view.height, self.map)

        # TODO: Sequencing and event handling effects need to be considered!
        # TODO: Currently an entity interaction doesn't count as a turn...
        def movePlayer(dx, dy):
            if player.tryMove(dx, dy):
                moveOthers()
                map.setDirty(True)

        self.view.addElement(frameStats)
        self.view.addElement(frameMessages)
        frameMessages.addElement(messages)
        self.view.addElement(map)

        # Inputs. =================================================================================
        self.view.setKeyInputs({
            'quit' : {
                'key' : Keys.Escape,
                'ch'  : None,
                'fn'  : sys.exit
            }
        })

        # TODO: This must be called after setKeyInputs on the element, or it will get blown away...
        map.setDirectionalInputHandler(movePlayer)
        self.setFocus(map)

        # Miscellany. =============================================================================
        import random
        random.seed(316)

        def moveOthers():
            for o in others:
                o.tryMove(random.randint(-1, 1), random.randint(-1, 1))

        # Event Handlers. =========================================================================
        # TODO: This could probably be foxified using decorators.
        def entityInteract(sender, e):
            other = e
            if sender == player:
                messages.message("You pet the %s for %d happiness." % (other.name, random.randint(2, 8)))
            elif other == player:
                messages.message("The %s baps you for %d fluff points." % (sender.name, random.randint(1,4)))
            else:
                messages.message("The %s stares down the %s." % (sender.name, other.name))
        self.map.on('entity_interact', entityInteract)

game = RoguePy.Game.Game("MiKeY SaYS SMiLe!", 96, 60, False)
game.addState(MainState('main'))
game.run('main')
