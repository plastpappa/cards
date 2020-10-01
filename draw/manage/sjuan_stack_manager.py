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
        
        self._sjuan_stack.listen(
            on_insert = lambda insert, card: insert.match(
                sjuan_insert = lambda: self._card_inserted(card)
            )
        )
        
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._drawer.pos = pos
        
        
    def _card_inserted(self, card):
        self._drawer._card_inserted(card)
        
    
    def draw(self):
        self._drawer.draw()
