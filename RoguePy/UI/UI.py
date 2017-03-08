'''
Documentation, License etc.

@package RoguePy
'''
import os
import sys
from RoguePy.libtcod import libtcod

class UI:
  _path = ''
  
  def __init__(self):
    self._rootPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    self._font = self._rootPath + b'/libtcod/dundalk12x12_gs_tc.png'#lucida10x10_gs_tc.png'
    self._renderer = libtcod.RENDERER_SDL
    
    self.width = None
    self.height = None
  
  def init(self, w, h, fs, title='RoguePy Game'):
    self.width = w
    self.height = h
    libtcod.console_set_custom_font(self._font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_init_root(w, h, title, fs, self._renderer)
  
  @property
  def width(self):
    return self.__width
  @width.setter
  def width(self,w):
    self.__width = w
  
  @property
  def height(self):
    return self.__height
  @height.setter
  def height(self,w):
    self.__height = w
  
  def refresh(self, view):
    view.renderElements()
    self._blitToRoot(view.getConsole(), view.x, view.y)
    libtcod.console_flush()
  
  def is_closed(self):
    closed = libtcod.console_is_window_closed()
    return closed
  
  def _blitToRoot(self, console, x, y):
    width = libtcod.console_get_width(console)
    height = libtcod.console_get_height(console)
    root = 0
    libtcod.console_blit(console, 0, 0, width, height, root, x, y)