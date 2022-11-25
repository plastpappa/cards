from typing import List

from card import *
from card.game import *

from draw.vector import Vector


def emit_event(objects: List[object], name: str, *args, **kwargs):
    for object in objects:
        method = getattr(object, name, None)
        if callable(method):
            method(*args, **kwargs)

class World:
    def __init__(self, parent):
        self._objects = []
        self._parent  = parent
        self._running = True


    @property
    def parent(self):
        return self._parent


    def add_object(self, object):
        self._objects.append(object)

        obj_init_world = getattr(object, 'init_world', None)
        if callable(obj_init_world):
            obj_init_world(self)
        else:
            object.world = self

    def remove_object(self, object):
        self._objects.remove(object)


    def game_over(self):
        self._running = False

    def draw(self):
        if self._running:
            emit_event(self._objects, 'draw')

    def mouse_at(self, x, y, dx, dy, button = 0, modifiers = 0):
        if self._running:
            emit_event(
                self._objects, 'mouse_at',
                Vector(x, y), Vector(dx, dy), button, modifiers
            )

    def mouse_down(self, x, y, button, modifiers):
        if self._running:
            emit_event(
                self._objects, 'mouse_down',
                Vector(x, y), button, modifiers
            )

    def mouse_up(self, x, y, button, modifiers):
        if self._running:
            emit_event(
                self._objects, 'mouse_up',
                Vector(x, y), button, modifiers
            )

    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._running:
            emit_event(
                self._objects, 'mouse_scroll',
                Vector(x, y), Vector(scroll_x, scroll_y)
            )
