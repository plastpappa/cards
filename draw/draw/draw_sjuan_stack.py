from pyglet.graphics import Batch

from card import *
from card.games.sjuan import *

from draw.draw import *
from draw.vector import Vector
from draw.arrow import Arrow


class SjuanStackDrawer:
    def __init__(
        self, sjuan_stack: SjuanCardStack, pos: Vector
    ):
        self._sjuan_stack = sjuan_stack
        self._pos = pos
