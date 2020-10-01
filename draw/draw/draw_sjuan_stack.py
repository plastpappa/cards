from copy import deepcopy

from pyglet.graphics import Batch

from card import *
from card.games.sjuan import *

from draw.draw import *
from draw.vector import Vector
from draw.arrow import Arrow
from draw.shape import RectangleShape
from draw.dashed_rect import DashedRect


class SjuanStackDrawer:
    PAD_X = (CardDrawer.CARD_SIZE.x + CardDrawer.CARD_SIZE.y) // 2 + 12
    
    def __init__(
        self, sjuan_stack: SjuanCardStack, pos: Vector
    ):
        self._sjuan_stack = sjuan_stack
        self._pos = pos
        self.visible = True
                
        self._batch_sevens = Batch()
        self._upper_batch  = Batch()
        self._lower_batch  = Batch()
        self._dotted_draws = {}
        self._seven_draws  = {}
        self._upper_draws  = {}
        self._lower_draws  = {}
        self._create_dotted_draws()
        
        # @TODO: For now we're assuming the sjuan stack is empty on init
        #        Not likely to be a big problem, but technically
        #        something to fix...
    
    
    def _create_dotted_draws(self):
        pad = 10
        dy  = CardDrawer.CARD_SIZE.y + pad
        
        pos = Vector(0, dy * (len(CardSuit) - 1) / 2)
        for suit in CardSuit:
            self._dotted_draws[suit] = DashedRect(
                RectangleShape(size   = CardDrawer.CARD_SIZE,
                               centre = deepcopy(pos)),
                dashes = [16, 8],
                batch  = self._batch_sevens
            )
            pos.y -= dy
        
    def _card_inserted(self, card):
        if card.value == CardValue.SEVEN:
            dotted_draw = self._dotted_draws[card.suit]
            draw = CardDrawer(
                card, dotted_draw.shape.centre,
                batch = self._batch_sevens
            )
            dotted_draw.delete()
            del dotted_draw
            self._seven_draws[card.suit] = draw
        else:
            seven = self._seven_draws[card.suit]
            
            if card.value.adj_value(aces_lowest = True) > CardValue.SEVEN.value:
                if card.suit in self._upper_draws:
                    self._upper_draws[card.suit].delete()
                self._upper_draws[card.suit] = CardDrawer(
                    card, Vector(-seven.pos.y, SjuanStackDrawer.PAD_X),
                    batch = self._upper_batch
                )
            else:
                if card.suit in self._lower_draws:
                    self._lower_draws[card.suit].delete()
                self._lower_draws[card.suit] = CardDrawer(
                    card, Vector(seven.pos.y, SjuanStackDrawer.PAD_X),
                    batch = self._lower_batch
                )
        
    
    def position_for(self, card):
        if card.value == CardValue.SEVEN:
            r = self._dotted_draws[card.suit].shape.centre
        elif card.value.adj_value(aces_lowest = True) > CardValue.SEVEN.value:
            r = self._seven_draws[card.suit].centre + Vector(
                SjuanStackDrawer.PAD_X, 0
            )
        else:
            r = self._seven_draws[card.suit].centre - Vector(
                SjuanStackDrawer.PAD_X, 0
            )
        return r + self._pos
        
        
    def draw(self):
        if self.visible:
            glPushMatrix()
            glTranslatef(self._pos.x, self._pos.y, 0)
            
            self._batch_sevens.draw()
            glRotatef(-90, 0.0, 0.0, 1.0)
            self._upper_batch.draw()
            glRotatef(180, 0.0, 0.0, 1.0)
            self._lower_batch.draw()
            
            glPopMatrix()
