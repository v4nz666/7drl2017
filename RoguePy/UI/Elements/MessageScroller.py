from RoguePy.libtcod import libtcod
from RoguePy.UI.Elements import Element

# TODO: Have a direction setting, so this can optionally scroll from the bottom up.
# TODO: Optionally change message color (fade) if they've sat in the scroller for an
#   option-specified length of time.
# TODO: Figure out the best / easiest / neatest way to get coloured text all up in here. Might be
#   a little tricky in conjunction with message fading.
class MessageScroller(Element):
  def __init__(self, x, y, w, h):
    super(MessageScroller, self).__init__(x, y, w, h)
    self.messages = []

  def message(self, text):
    last = self._addOrStack(text)
    last.height = self.getTextHeight(last.getText())
    # Cull messages when the thingy is full.
    # TODO: Should this thing perhaps preserve the entire message history, and only cull the displayed
    #   thinger? That way you could browse the entire message history, if you so desired...
    n = 0
    h = 0
    for i in reversed(self.messages):
      if ( i.height == None ):
        raise Exception("%s height not set before culling iteration!" % i)
      n += 1
      h += i.height
      if h >= self.height:
        break
    self.messages = self.messages[-n:]
    self.setDirty(True)

  def _addOrStack(self, text):
    # Handle message stacking.
    if len(self.messages) > 0:
      last = self.messages[-1]
      if last.text == text:
        last.count += 1
        return last
    # Normal message appending.
    self.messages.append(Item(text))
    return self.messages[-1]

  def getTextHeight(self, text):
    return libtcod.console_get_height_rect(self.console, 0, 0, self.width, 0, text)

  def draw(self):
    # TODO: Setting this to -1 results in a multi-line string not getting rendered at all, rather
    #   than rendering the not-cut-off bit, as one might expect. Need a fix for this, or partially
    #   cut-off messages will disappear and leave a stupid gap.
    y = 0
    for i in self.messages:
      h = i.height
      if ( h == None ):
        raise Exception("%s height not set before MessageScroller.draw() was called!" % i)
      libtcod.console_print_rect(self.console, 0, y, self.width, h, i.getText())
      y += h
    self.setDirty(False)



class Item:
  def __init__(self, text):
    self.text = text
    self.count = 1
    self.height = None;

  def __repr__(self):
    return "Item('%s', n=%d, h=%d)" % (self.text, self.count, self.height)

  def getText(self):
    result = '> ' + self.text
    if self.count > 1:
      result += ' x %d' % self.count
    return result
