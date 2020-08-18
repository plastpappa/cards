from typing import Callable

from pyglet.graphics import Batch

from card import *
from draw.draw import *
from draw.vector import Vector
from draw.arrow import Arrow


class FloatingCardManager:
    def __init__(
        self, card: Card, mouse_pos: Vector,
        origin: Vector, on_death: Callable,
        batch = None, group = None
    ):
        if batch:
            self.batch = batch
            self.batch_is_own = False
        else:
            self.batch = Batch()
            self.batch_is_own = True
        self.group_back  = OrderedGroup(0, group)
        self.group_front = OrderedGroup(1, group)
        
        def div(x, y):
            return math.copysign(math.inf, x) if y == 0 else x / y
        
        pos = self.position_for(mouse_pos)
        self.drawer = CardDrawer(
            card, pos, targeted = True,
            batch = self.batch, group = self.group_back
        )
        
        self.arrow = Arrow(
            pos, origin,
            colour = (126, 178, 212, 168), stroke_width = 3,
            arrow_size = 0, pad = 0, offset = 0,
            batch = self.batch, group = self.group_front
        )
        
        self.origin   = origin
        self.on_death = on_death
        
        self.redraw_change_pos = None
        
    
    def position_for(self, mouse_pos: Vector):
        return mouse_pos + Vector(0, 4 - CardDrawer.CARD_SIZE.y // 2)
        
    
    def draw(self):
        if self.redraw_change_pos:
            pos = self.position_for(self.redraw_change_pos)
            self.drawer.pos        = pos
            self.redraw_change_pos = None
            self.arrow._posA       = pos
            sqrt_dist = (pos - self.origin).magnitude() ** 0.7
            self.arrow._arrow_size = 30 + sqrt_dist / 6
            self.arrow._pad        = 2  + sqrt_dist / 3
            self.arrow._offset     = 3  + sqrt_dist / 28
            self.arrow._update()
        
        if self.batch_is_own:
            self.batch.draw()
        else:
            self.drawer.draw()
            self.line.draw()

        
    def mouse_at(self, mouse_pos, delta, button, modifiers):
        self.redraw_change_pos = mouse_pos

    def mouse_up(self, mouse_pos, button, modifiers):
        self.on_death()
        self.world.remove_object(self)
