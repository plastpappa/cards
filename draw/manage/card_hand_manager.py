from functools import partial

from card import *
from draw.draw import *
from draw.vector import Vector
from draw.manage import World, FloatingCardManager


class CardHandManager:
    def __init__(self, hand: CardHand, pos: Vector, label: str):
        self._hand  = hand
        self._pos   = pos
        self._label = label
        
        self._drawer          = CardRowDrawer(hand.cards, pos, label = label)
        self.targeted_card    = None
        self.is_card_floating = False
    
    
    @property
    def pos(self):
        return self._pos
        
    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._drawer.pos = pos
    
    @property
    def label(self):
        return self._label
        
    @label.setter
    def label(self, label):
        self._label = label
        self._drawer.label = label
        
    @property
    def rotation(self):
        return self._drawer.rotation
        
    @rotation.setter
    def rotation(self, rotation):
        self._drawer.rotation = rotation
    
    
    def get_card_index_at(self, pos: Vector):
        if self._drawer.bounds_inner.has_point(pos):
            for i, card_draw in enumerate(self._drawer._card_draws):
                if card_draw.has_point(pos):
                    return i
        return None
        
    def set_target(self, target):
        if self.targeted_card != target:
            if self.targeted_card is not None:
                self._drawer._card_draws[self.targeted_card].targeted = False
            if target is not None:
                self._drawer._card_draws[target].targeted = True
            self.targeted_card = target
        
    def draw(self):
        self._drawer.draw()
    
    def mouse_at(self, mouse_pos, delta, button, modifiers):
        if not self.is_card_floating:
            self.set_target(self.get_card_index_at(mouse_pos))
            
    def mouse_down(self, mouse_pos, button, modifiers):
        def readd_card(card_draw):
            card_draw.transparent = False
            self.is_card_floating = False
        
        if self.targeted_card:
            card      = self._drawer._cards[self._drawer.offset + self.targeted_card]
            card_draw = self._drawer._card_draws[self.targeted_card]
            self.world.add_object(FloatingCardManager(
                card, mouse_pos, origin = card_draw.pos,
                on_death = partial(readd_card, card_draw = card_draw)
            ))
            card_draw.targeted = False
            card_draw.transparent = True
            self.targeted_card = None
            self.is_card_floating = True
            
    def mouse_scroll(self, mouse_pos, scroll):
        if self._drawer.bounds_inner.has_point(mouse_pos):
            self.set_target(None)
                            
            if scroll.y > 0:
                self._drawer.incr_offset()
            else:
                self._drawer.decr_offset()
            
            self.mouse_at(mouse_pos, Vector(0, 0), 0, 0)
