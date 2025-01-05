from copy import deepcopy

from pyglet import shapes as shp, text as txt, font
from pyglet.graphics import Batch

from card import *
from draw.draw import *
from draw.vector import Vector


class CardStackDrawer:
    LABEL_HOVER      = Vector(0, 14)
    LABEL_BG_PADDING = Vector(10, 1)
    LABEL_BG_COLOUR  = (160, 188, 255, 120)
    TEXT_COLOUR      = (255, 255, 255, 170)
        
    def __init__(
        self, cards: List[Card], pos: Vector, label: str,
        top_hidden: bool = True,
        batch = None, group = None
    ):
        self._pos   = pos
        self._cards = deepcopy(cards)
        self._label = label
        self._top_hidden = top_hidden
        if batch is None:
            self._batch = Batch()
            self._batch_is_own = True
        else:
            self._batch = batch
            self._batch_is_own = False
        self._group = group
        
        self._card_draw = None
        self._labels    = []
        self._update()
    
    
    @property
    def cards(self):
        return self._cards
        
    @cards.setter
    def cards(self, cards):
        old_cards_len = len(self._cards)
        self._cards = deepcopy(cards)
        lens_diff = old_cards_len != len(cards)
        
        if lens_diff:
            self._update_label()
        
        if ((not self._top_hidden and cards[0] != self._cards[0])
           or (lens_diff and (len(cards) == 0 or old_cards_len == 0))):
            self._update_card_draw()
    
            
    def _update_card_draw(self):
        self._delete_card_draw()
        if len(self._cards) > 0:
            self._card_draw = CardDrawer(
                self._cards[0], self._pos,
                hidden = self._top_hidden,
                batch = self._batch, group = self._group
            )
            
    def _update_label(self):
        self._delete_label()
        
        if self._label:
            info = LabelWithBackground(
                f"{len(self._cards)} cards",
                colour = CardStackDrawer.TEXT_COLOUR,
                background_colour = CardStackDrawer.LABEL_BG_COLOUR,
                background_padding = CardStackDrawer.LABEL_BG_PADDING,
                pos = self._card_draw.top_centre + CardStackDrawer.LABEL_HOVER,
                anchor_x = 'center', anchor_y = 'bottom',
                font_name = 'Source Code Pro', font_size = 10,
                batch = self._batch, group = self._group
            )
            
            name = LabelWithBackground(
                self._label,
                colour = CardRowDrawer.TEXT_COLOUR,
                background_colour = CardRowDrawer.LABEL_BG_COLOUR,
                background_padding = CardRowDrawer.LABEL_BG_PADDING,
                pos = info.bounds.top_centre + Vector(0, 5),
                anchor_x = 'center', anchor_y = 'bottom',
                font_name = 'Source Code Pro', font_size = 10,
                batch = self._batch, group = self._group
            )
            
            self._top_labels = [info, name]
    
    def _update(self):
        self._update_card_draw()
        self._update_label()
        
    
    def _delete_card_draw(self):
        if self._card_draw:
            self._card_draw.delete()
            self._card_draw = None
            
    def _delete_label(self):
        for label in self._labels:
            label.delete()
        self._labels = []
    
    def delete(self):
        self._delete_card_draw()
        
        
    def draw(self):
        if self._batch_is_own:
            self._batch.draw()
        else:
            self._card_draw.draw()
            for label in self._labels:
                label.draw()
