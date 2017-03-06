'''
Documentation, License etc.

@package RoguePy.UI
'''
from RoguePy.libtcod import libtcod

class View(object):

  def __init__(self, w, h, x=0, y=0 ):

    self.width = w
    self.height = h
    self.x = x
    self.y = y

    self.setDirty(True)

    self._elements = []

    self._keyBoardInputs = {}
    self._mouseInputs = {
      'rClick': None,
      'lClick': None
    }

    self._storedEnabled = None
    
    self.console = libtcod.console_new(self.width, self.height)
    self.inputsEnabled = True
    self.fg = libtcod.white
    self.bg = libtcod.black

  def clearAll(self):

    self.clear()

    for e in self._elements:
      e.clearAll()
    self._elements = []
    self._keyBoardInputs = {}

  def getElements(self):
    return self._elements
  
  def getConsole(self):
    return self.console
  
  def addElement(self, el):
    if el.x + el.width >= self.width:
      el.width = self.width - el.x
    if el.y + el.height>= self.height:
      el.height = self.height - el.y

    self._elements.append(el)
    el.setParent(self)
    return el
  def removeElement(self, el):
    if el in self._elements:
      self._elements.remove(el)
    self.setDirty()
  
  def setKeyInputs(self, inputs):
    """
    Set the keyboard inputs to be bound to this View/Element

    :param inputs: Dictionary of input definitions. Takes the format:
      {
        'quit': {
          'key': libtcod.KEY_ESCAPE,
          'char': None,
          'fn': self.quitCallback
        },
        ...,
        'goNorth': {
          'key': libtcod.KEY_CHAR,
          'char': 'n',
          'fn': self.move
        },
        ...
      }
    """
    self._keyBoardInputs = inputs


  def setMouseInputs(self, inputs):
    self._mouseInputs = inputs


  def getInputs(self):

    return self._keyBoardInputs
  
  def storeState(self):
    """
    Store the enabled status of all elements. This method must be called prior to calling restoreState. Use this method
      in conjunction with the disableAll method to put the view into "modal" mode, by calling them, then manually
      enabling an element.


    :return: None
    """
    self._storedEnabled = []
    index = 0
    for e in self._elements:
      if e.enabled:
        self._storedEnabled.append(index)
      index += 1
  def restoreState(self):
    """
    Restore the enabled state of all elements previously stored via storeState.

    :raise Exception: When called before a call to storeState.
    """
    if not self._storedEnabled:
      raise Exception("You must call storeState before calling restoreState.")
    for index in self._storedEnabled:
      self._elements[index].enable()
  
  def disableAll(self, disableSelf=True):
    """
    Disable all elements. Disabled elements are rendered with a low-opacity overlay of their bg color.

    :param disableSelf: Also disable the Inputs bound directly to the View? Defaults to True
    """
    for e in self._elements:
      e.disable()
    if disableSelf:
      self.disableInputs()
  
  def enableInputs(self):
    self.inputsEnabled = True
  def disableInputs(self):
    self.inputsEnabled = False
  
  def getActiveInputs(self, _inputs={}, el=None):
    """
    Recursive function to get the inputs of our self, and all active elements.

    :param _inputs: The inputs we've gathered so far
    :param el: The current element we're working on
    :return: The full list of all active Inputs
    """
    if el is None:
      el = self
      keyInputs = {}
    else:
      keyInputs = _inputs
    if ( el == self ) or ( el.visible and el.enabled ):
      if ( el == self and self.inputsEnabled ) or el != self:
        newInputs = el.getInputs()
        keyInputs.update(newInputs)

      for e in el.getElements():
        self.getActiveInputs(keyInputs, e)
    if el == self:
      return keyInputs, self._mouseInputs

  def setDirty(self, dirty=True):
    self._dirty = dirty
    return self

  def isDirty(self):
    return self._dirty


  def setDefaultForeground(self, fg, cascade=False):
    self.fg = fg
    libtcod.console_set_default_foreground(self.console,fg)

    if cascade:
      for e in self._elements:
        e.setDefaultForeground(fg, True)

    self.setDirty()
    return self

  def setDefaultBackground(self, bg, cascade=False):
    self.bg = bg
    libtcod.console_set_default_background(self.console,bg)
    if cascade:
      for e in self._elements:
        e.setDefaultBackground(bg, True)

    self.setDirty()
    return self

  #TODO Convert fg, bg to a tuple
  def setDefaultColors(self, fg = libtcod.white, bg = libtcod.black, cascade=False):
    self.setDefaultForeground(fg, cascade)
    self.setDefaultBackground(bg, cascade)
    return self
  
  def getDefaultColors(self):
    return self.fg, self.bg

  ###
  # Drawing methods
  ###

  def clear(self):
    libtcod.console_clear(self.console)
    self.setDirty()
    return self

  def putCh(self, x, y, ch, fg, bg):
    libtcod.console_put_char_ex(self.console, x, y, ch, fg, bg)
    self.setDirty()
    
  def renderElements(self):
    for e in self._elements:
      if not e.visible:
        continue
      if e.isDirty():
        e.clear()
        e.draw()
      e.renderElements()
      if not e.enabled:
        self.renderOverlay(e)
      libtcod.console_blit(e.console, 0, 0, e.width, e.height, self.console, e.x, e.y, e.fgOpacity, e.bgOpacity)

  def getDefaultForeGround(self):
    return libtcod.console_get_default_foreground(self.console)

  @staticmethod
  def renderOverlay(el):
    if not (el.width and el.height):
      return
    con = libtcod.console_new(el.width, el.height)
    libtcod.console_set_default_background(con, el.bg)
    libtcod.console_clear(con)
    libtcod.console_blit(con, 0, 0, el.width, el.height, el.console, 0, 0, 0.0, 0.4)
    libtcod.console_delete(con)

    el.setDirty()
