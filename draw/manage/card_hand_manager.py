from functools import partial

from pyglet import text as txt

from card import *
from draw.draw import *
from draw.vector import Vector
from draw.manage import World, FloatingCardManager


class CardHandManager:
    def __init__(self, hand: CardHand, pos: Vector, label: str):
        self._hand  = hand
        self._pos   = pos
        self._label = label
        
        self._update = False
        hand.listen(
            on_take   = lambda take: take.match(
                hand_take = lambda i: self._card_taken(i)
            ),
            on_insert = lambda insert, card: insert.match(
                hand_insert = lambda i: self._card_inserted(i, card)
            )
        )
        
        self._drawer = CardRowDrawer(hand.cards, pos, label = label)
        self._draw_info     = None
        self.targeted_card  = None
        self._floating_card = None
        self._floating_origin = None
        self.controllable   = False
        self.world          = None
    
        
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
    
    
    def _card_taken(self, i):
        self._drawer.card_taken(i)
        
    def _card_inserted(self, i, card):
        self._drawer.card_inserted(i, card)
    
        
    def get_card_index_at(self, pos: Vector):
        if self._drawer.bounds_inner.has_point(pos):
            for i, card_draw in self._drawer.displayed_cards_with_index():
                if card_draw.has_point(pos):
                    return i
        return None
        
    def set_target(self, target):
        if self.targeted_card != target:
            if self._draw_info is not None:
                self._draw_info.delete()
            
            if self.targeted_card is not None:
                self._drawer.nth_card(self.targeted_card).targeted = False
            if target is not None:
                self._draw_info = txt.Label(
                    str(self._drawer.nth_card(target).card),
                    font_name = 'Source Code Pro', font_size = 12,
                    x = self._pos.x, y = self._pos.y + 100,
                    anchor_x = 'center',
                    batch = self._drawer._batch
                )
                            
                self._drawer.nth_card(target).targeted = True
            self.targeted_card = target
        
    
    def draw(self):
        if self._update:
            self._update = False
            self._drawer.cards = self._hand.cards
        self._drawer.draw()
    
    def mouse_at(self, mouse_pos, delta, button, modifiers):
        if self.controllable and not self._floating_card:
            self.set_target(self.get_card_index_at(mouse_pos))
            
    def mouse_down(self, mouse_pos, button, modifiers):
        def readd_card(card_i):
            card_draw = self._drawer.nth_card(card_i)
            if card_draw:
                card_draw.transparent = False
            self._floating_card = None
            
        def delete_card(card_i, move):
            self._floating_card = None
        
        if self.controllable and self.targeted_card is not None:
            i     = self.targeted_card
            card  = self._drawer._cards[i]
            
            card_draw = self._drawer.nth_card(i)
            self._floating_card = FloatingCardManager(
                card, mouse_pos, origin = card_draw.pos,
                moves = self.world.parent.moves_for_card(i),
                on_readd = partial(readd_card,  i),
                on_bye   = partial(delete_card, i)
            )
            self._floating_origin = self.targeted_card
            self.world.add_object(self._floating_card)
            card_draw.targeted = False
            card_draw.transparent = True
            self.targeted_card = None
            
    def mouse_scroll(self, mouse_pos, scroll):
        if (
            self._drawer.bounds_inner.has_point(mouse_pos)
            or self._floating_card
        ):
            self.set_target(None)
                            
            if scroll.y > 0:
                self._drawer.incr_offset()
            else:
                self._drawer.decr_offset()
            
            if self._floating_card:
                self._floating_card.moves = self.world.parent.moves_for_card(
                    self._floating_origin
                )
                self._floating_card.origin = (
                    self._drawer.nth_card(self._floating_origin).pos
                )
            
            self.mouse_at(mouse_pos, Vector(0, 0), 0, 0)
