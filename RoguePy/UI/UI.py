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
    self._font = self._rootPath + b'/libtcod/lucida10x10_gs_tc.png'
    self._renderer = libtcod.RENDERER_SDL
    
    self._width = None
    self._height = None
  
  def init(self, w, h, fs, title='RoguePy Game'):
    self._width = w
    self._height = h
    libtcod.console_set_custom_font(self._font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_init_root(w, h, title, fs, self._renderer)
  
  def getWidth(self):
    return self._width
  
  def getHeight(self):
    return self._height
  
  def refresh(self, view):
    # TODO doesnt' seem this is necessary?! I don't think we want to be doing it, if not...
    #view.clear()
    view.renderElements()
    self._blitToRoot(view.getConsole())
    libtcod.console_flush()
  
  def is_closed(self):
    closed = libtcod.console_is_window_closed()
    return closed
  
  def _blitToRoot(self, console):
    width = libtcod.console_get_width(console)
    height = libtcod.console_get_height(console)
    root = 0
    libtcod.console_blit(console, 0, 0, width, height, root, 0, 0)