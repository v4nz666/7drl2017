from RoguePy.libtcod import libtcod

class InputHandler():

  def __init__(self):
      self.key = libtcod.Key()
      self.mouse = libtcod.Mouse()

      self.setKeyInputs({})
      self.mouseInputs = {
          'rClick': None,
          'lClick': None
      }

      self.gotInput = False

  def gotInput(self):
    return False

  def handleInput(self):
      self.gotInput = False

      libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS,
                                  self.key, self.mouse)

      if self.key.vk != libtcod.KEY_NONE:
          self.handleKeyInput(self.key)
          self.gotInput = True

      if self.mouse.rbutton_pressed:
          if self.mouseInputs['rClick']:
              self.mouseInputs['rClick'](self.mouse)
              self.gotInput = True

      if self.mouse.lbutton_pressed:
          if self.mouseInputs['lClick']:
              self.mouseInputs['lClick'](self.mouse)
              self.gotInput = True


  def handleKeyInput(self, key):
      for name in self.keyInputs:
          cmd = self.keyInputs[name]
          if (cmd['key'] and (cmd['key'] == key.vk or str(cmd['key']).lower() == "any")) or (
                      cmd['ch'] and (ord(cmd['ch'].lower()) == key.c or ord(cmd['ch'].upper()) == key.c)):
              return cmd['fn']()
      return self

  def addKeyInputs(self, inputs):
      for i in inputs:
          self.keyInputs[i] = inputs[i]

  def setKeyInputs(self, inputs):
      self.keyInputs = {}
      self.addKeyInputs(inputs)

  def setMouseInputs(self, inputs):
      for i in inputs:
          if i in ['rClick', 'lClick']:
              self.mouseInputs[i] = inputs[i]
      return self.mouseInputs
