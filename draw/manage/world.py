from typing import List

from card import *

from draw.vector import Vector


def emit_event(objects: List[object], name: str, *args, **kwargs):
    for object in objects:
        method = getattr(object, name, None)
        if callable(method):
            method(*args, **kwargs)
    
class World:
    def __init__(self):
        self._objects = []
    
    
    def add_object(self, object):
        self._objects.append(object)
        
        obj_init_world = getattr(object, 'init_world', None)
        if callable(obj_init_world):
            obj_init_world(self)
        else:
            object.world = self
    
    def remove_object(self, object):
        self._objects.remove(object)
        
    
    def draw(self):
        emit_event(self._objects, 'draw')
        
    def mouse_at(self, x, y, dx, dy, button = 0, modifiers = 0):
        emit_event(
            self._objects, 'mouse_at',
            Vector(x, y), Vector(dx, dy), button, modifiers
        )
        
    def mouse_down(self, x, y, button, modifiers):
        emit_event(
            self._objects, 'mouse_down',
            Vector(x, y), button, modifiers
        )
        
    def mouse_up(self, x, y, button, modifiers):
        emit_event(
            self._objects, 'mouse_up',
            Vector(x, y), button, modifiers
        )
        
    def mouse_scroll(self, x, y, scroll_x, scroll_y):
        emit_event(
            self._objects, 'mouse_scroll',
            Vector(x, y), Vector(scroll_x, scroll_y)
        )
