from pyglet.graphics import Batch

from card import *
from card.games.sjuan import *

from draw.draw import *
from draw.vector import Vector
from draw.arrow import Arrow


class SjuanStackManager:
    def __init__(
        self, sjuan_stack: SjuanCardStack, pos: Vector
    ):
        self._sjuan_stack = sjuan_stack
        self._pos = pos
        
        self._drawer = SjuanStackDrawer(self._sjuan_stack, self._pos)
        
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._drawer.pos = pos
