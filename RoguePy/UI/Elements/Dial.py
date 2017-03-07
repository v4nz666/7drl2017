'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element, List


class Dial(Element):

    def __init__(self, x, y, size='s'):
        if size not in ['l', 's']:
            raise Exception("Size must be 'l' or 's'")

        self.cacheFaces()

        wh = len(self.faces[size][0])
        super(Dial, self).__init__(x, y, wh, wh)

        self.size = size
        self.min = 0
        self.max = 360
        self.val = 0

        self.face = self.faces[self.size][0]
        self.list = self.addElement(List(0, 0, len(self.face), len(self.face), self.face))

    def setMin(self, min):
        self.min = min

    def setMax(self, max):
        self.max = max

    def setVal(self, val):

        if val < 0:
            val += self.max
        elif val >= self.max:
            val -= self.max

        self.val = val
        faceIndex = int((self.val + 11.25) / 22.5)
        if faceIndex == len(self.faces[self.size]):
            faceIndex = 0
        self.face = self.faces[self.size][faceIndex]
        self.setDirty(True)

    def getVal(self):
        return self.val

    def sub(self, deg):
        self.setVal(self.val + deg)
        self.setDirty(True)

    def add(self, deg):
        self.setVal(self.val - deg)
        self.setDirty(True)

    def draw(self):
        self.list.setItems(self.face)
        self.setDirty(False)

    def setDefaultForeground(self, fg, cascade=True):
        super(Dial, self).setDefaultForeground(fg, cascade)
        return self

    def setDefaultBackground(self, bg, cascade=True):
        super(Dial, self).setDefaultBackground(bg, cascade)
        return self

    def cacheFaces(self):
        self.faces = {
            'l':
                [
                [  # 348.75 - 11.25
                    '/     \\',
                    '       ',
                    '       ',
                    '   +---',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 11.25 - 33.75
                    '/     \\',
                    '       ',
                    '     --',
                    '   +-  ',
                    '       ',
                    '       ',
                    '\\     /'
                ],

                [  # 33.75 - 56.25
                    '/     \\',
                    '     / ',
                    '    /  ',
                    '   +   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 56.25 - 78.75
                    '/   | \\',
                    '    |  ',
                    '   |   ',
                    '   +   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 78.75 - 101.25
                    '/  |  \\',
                    '   |   ',
                    '   |   ',
                    '   +   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 101.25 - 123.75
                    '/ |   \\',
                    '  |    ',
                    '   |   ',
                    '   +   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 123.75 - 146.25
                    '/     \\',
                    ' \\     ',
                    '  \\    ',
                    '   +   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 146.25 - 168.75
                    '/     \\',
                    '--     ',
                    '  -    ',
                    '   +   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 168.75 - 191.25
                    '/     \\',
                    '       ',
                    '       ',
                    '---+   ',
                    '       ',
                    '       ',
                    '\\     /'
                ],
                [  # 191.25 - 213.75
                    '/     \\',
                    '       ',
                    '       ',
                    '   +   ',
                    '  -    ',
                    '--     ',
                    '\\     /'
                ],
                [  # 213.75 - 236.25
                    '/     \\',
                    '       ',
                    '       ',
                    '   +   ',
                    '  /    ',
                    ' /     ',
                    '\\     /'
                ],
                [  # 236.25 - 258.75
                    '/     \\',
                    '       ',
                    '       ',
                    '   +   ',
                    '   |   ',
                    '  |    ',
                    '\\ |   /'
                ],
                [  # 258.75 - 281.25
                    '/     \\',
                    '       ',
                    '       ',
                    '   +   ',
                    '   |   ',
                    '   |   ',
                    '\\  |  /'
                ],
                [  # 281.25 - 303.75
                    '/     \\',
                    '       ',
                    '       ',
                    '   +   ',
                    '   |   ',
                    '    |  ',
                    '\\   | /'
                ],
                [  # 303.75 - 326.25
                    '/     \\',
                    '       ',
                    '       ',
                    '   +   ',
                    '    \\  ',
                    '     \\ ',
                    '\\     /'
                ],
                [  # 326.25 - 348.75
                    '/     \\',
                    '       ',
                    '       ',
                    '   +-  ',
                    '     --',
                    '       ',
                    '\\     /'
                ]
            ],
            's':
                [
                [  # 348.75 - 11.25
                    '/   \\',
                    '     ',
                    '  +--',
                    '     ',
                    '\\   /'
                ],
                [  # 11.25 - 33.75
                    '/   \\',
                    '    -',
                    '  +- ',
                    '     ',
                    '\\   /'
                ],

                [  # 33.75 - 56.25
                    '/   \\',
                    '   / ',
                    '  +  ',
                    '     ',
                    '\\   /'
                ],
                [  # 56.25 - 78.75
                    '/  |\\',
                    '  |  ',
                    '  +  ',
                    '     ',
                    '\\   /'
                ],
                [  # 78.75 - 101.25
                    '/ | \\',
                    '  |  ',
                    '  +  ',
                    '     ',
                    '\\   /'
                ],
                [  # 101.25 - 123.75
                    '/|  \\',
                    '  |  ',
                    '  +  ',
                    '     ',
                    '\\   /'
                ],
                [  # 123.75 - 146.25
                    '/   \\',
                    ' \\   ',
                    '  +  ',
                    '     ',
                    '\\   /'
                ],
                [  # 146.25 - 168.75
                    '/   \\',
                    '-    ',
                    ' -+  ',
                    '     ',
                    '\\   /'
                ],
                [  # 168.75 - 191.25
                    '/   \\',
                    '     ',
                    '--+  ',
                    '     ',
                    '\\   /'
                ],
                [  # 191.25 - 213.75
                    '/   \\',
                    '     ',
                    ' -+  ',
                    '-    ',
                    '\\   /'
                ],
                [  # 213.75 - 236.25
                    '/   \\',
                    '     ',
                    '  +  ',
                    ' /   ',
                    '\\   /'
                ],
                [  # 236.25 - 258.75
                    '/   \\',
                    '     ',
                    '  +  ',
                    '  |  ',
                    '\\|  /'
                ],
                [  # 258.75 - 281.25
                    '/   \\',
                    '     ',
                    '  +  ',
                    '  |  ',
                    '\\ | /'
                ],
                [  # 281.25 - 303.75
                    '/   \\',
                    '     ',
                    '  +  ',
                    '  |  ',
                    '\\  |/'
                ],
                [  # 303.75 - 326.25
                    '/   \\',
                    '     ',
                    '  +  ',
                    '   \  ',
                    '\\   /'
                ],
                [  # 326.25 - 348.75
                    '/   \\',
                    '     ',
                    '  +- ',
                    '    -',
                    '\\   /'
                ]
            ]
        }
